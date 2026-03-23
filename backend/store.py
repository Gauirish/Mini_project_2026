import json
import os
import psycopg2
import requests
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel
import math
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
def get_db_connection():
    return psycopg2.connect(
        host="aws-1-ap-southeast-2.pooler.supabase.com",
        database="postgres",
        user="postgres.apdzemtysvmlojlwkjxu",
        password="souravgenshin",
        port="5432",
        sslmode="require",
        # Prevent frontend "frozen" loading when the DB is slow/unreachable.
        connect_timeout=8,
        # Hard limit to avoid long-running queries.
        options="-c statement_timeout=20000"
    )

# =========================
# AI REVIEW ENDPOINT
# =========================

class ReviewRequest(BaseModel):
    movie_id: str
    review: str
    user_id: str = None
    user_name: str = "Anonymous"


@app.post("/analyze-review")
def analyze_review(data: ReviewRequest):

    try:
        from model import analyze
    except ImportError:
        return {
            "error": "AI analysis model is not ready. Please install dependencies."
        }

    # Run sentiment analysis
    result = analyze(data.review)

    # If meaningless, don't store and return error
    if result.get("is_meaningless", False):
        return {
            "error": "Meaningless Review",
            "message": result.get("message", "Your review seems to be meaningless."),
            "is_meaningless": True
        }

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert review
    cursor.execute("""
        INSERT INTO reviews (movie_id, review_text, rating, sentiment, aspects, user_id, user_name, is_spam)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """, (
        data.movie_id,
        data.review,
        result["rating"],
        result["sentiment"],
        json.dumps(result["aspects"]),
        data.user_id,
        data.user_name,
        result.get("is_spam", False)
    ))

    review_id = cursor.fetchone()[0]

    # Only update movie average rating if NOT spam
    if not result.get("is_spam", False):
        cursor.execute("""
            UPDATE movies
            SET avg_rating = (
                SELECT COALESCE(AVG(rating),0)
                FROM reviews
                WHERE movie_id=%s AND is_spam=FALSE
            )
            WHERE id=%s;
        """, (data.movie_id, data.movie_id))

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "review_id": review_id,
        "rating": result["rating"],
        "sentiment": result["sentiment"],
        "aspects": result["aspects"],
        "is_spam": result.get("is_spam", False),
        "message": result.get("message")
    }

# =========================
# AGGREGATED ASPECTS ENDPOINT
# =========================

@app.get("/movie-reviews/{movie_id}")
def get_movie_reviews_list(movie_id: str, limit: int = 5, offset: int = 0):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, review_text, rating, sentiment, aspects, user_name, created_at
        FROM reviews
        WHERE movie_id = %s AND (is_spam = FALSE OR is_spam IS NULL)
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """, (movie_id, limit, offset))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    reviews = []
    for row in rows:
        reviews.append({
            "id": row[0],
            "text": row[1],
            "rating": row[2],
            "sentiment": row[3],
            "aspects": json.loads(row[4]) if isinstance(row[4], str) else row[4],
            "user_name": row[5] or "Anonymous",
            "created_at": row[6].isoformat() if row[6] else None
        })
    return reviews


@app.get("/movie-aspects/{movie_id}")
def get_movie_aspects(movie_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT aspects
        FROM reviews
        WHERE movie_id = %s AND (is_spam = FALSE OR is_spam IS NULL)
    """, (movie_id,))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    aggregated = {
        "acting": [],
        "story": [],
        "music": [],
        "direction": [],
        "visuals": []
    }

    for row in rows:
        aspects = row[0]
        if isinstance(aspects, str):
            aspects = json.loads(aspects)

        if aspects:
            for key in aggregated:
                val = aspects.get(key)
                if key == "music" and val is None:
                    val = aspects.get("bgm")
                
                if val is not None:
                    aggregated[key].append(val)

    averaged = {}
    for key, values in aggregated.items():
        if values:
            averaged[key] = round(sum(values) / len(values), 1)
        else:
            averaged[key] = 0

    return averaged

# =========================
# GET MOVIES
# =========================

@app.get("/movies")
def get_movies():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, tmdb_id, title, poster_path, release_date, overview, avg_rating
        FROM movies
        ORDER BY release_date DESC;
    """)

    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    movies = []
    for row in rows:
        movie = dict(zip(columns, row))
        # Safeguard: Convert NaN avg_rating to 0
        if movie.get("avg_rating") is not None and math.isnan(movie["avg_rating"]):
            movie["avg_rating"] = 0.0
        movies.append(movie)

    cursor.close()
    conn.close()

    return movies


@app.get("/")
def root():
    return {"status": "Backend running"}

# =========================
# GET HIGHLIGHT REVIEWS
# =========================

@app.get("/movie-highlights/{movie_id}")
def get_movie_highlights(movie_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get latest positive review
    cursor.execute("""
        SELECT review_text
        FROM reviews
        WHERE movie_id = %s AND sentiment = 'positive'
        ORDER BY created_at DESC
        LIMIT 1;
    """, (movie_id,))
    positive = cursor.fetchone()

    # Get latest negative review
    cursor.execute("""
        SELECT review_text
        FROM reviews
        WHERE movie_id = %s AND sentiment = 'negative'
        ORDER BY created_at DESC
        LIMIT 1;
    """, (movie_id,))
    negative = cursor.fetchone()

    cursor.close()
    conn.close()

    return {
        "positive": positive[0] if positive else None,
        "negative": negative[0] if negative else None
    }

# =========================
# MOVIE SYNC (TMDB)
# =========================

@app.get("/sync")
def sync_movies():
    """Fetches movies released today from TMDB and adds them to the database."""
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        return {"error": "TMDB_API_KEY missing"}

    today = datetime.now().strftime("%Y-%m-%d")
    tmdb_url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": api_key,
        "with_original_language": "ml",
        "primary_release_date.gte": "2026-03-18",
        "primary_release_date.lte": today,
        "language": "en-US",
        "sort_by": "popularity.desc"
    }

    try:
        response = requests.get(tmdb_url, params=params)
        response.raise_for_status()
        movies = response.json().get("results", [])
    except Exception as e:
        return {"error": str(e)}

    conn = get_db_connection()
    cursor = conn.cursor()
    added_count = 0

    for movie in movies:
        tmdb_id = movie.get("id")
        title = movie.get("title")
        poster_path = movie.get("poster_path")
        release_date = movie.get("release_date")
        overview = movie.get("overview")
        genre_ids = movie.get("genre_ids", []) # TMDB returns genre ids

        cursor.execute("SELECT id FROM movies WHERE tmdb_id = %s", (str(tmdb_id),))
        if cursor.fetchone():
            continue

        cursor.execute("""
            INSERT INTO movies (tmdb_id, title, poster_path, release_date, overview, avg_rating)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (str(tmdb_id), title, poster_path, release_date, overview, 0))
        added_count += 1

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "success", "added_movies": added_count, "date": today}

# =========================
# GET USER REVIEWS
# =========================

@app.get("/user-reviews/{user_id}")
def get_user_reviews(user_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Join reviews with movies to get poster and title
    cursor.execute("""
        SELECT 
            r.id, r.review_text, r.rating, r.sentiment, r.created_at,
            m.title, m.poster_path, m.id as movie_id
        FROM reviews r
        JOIN movies m ON r.movie_id = m.id
        WHERE r.user_id = %s
        ORDER BY r.created_at DESC;
    """, (user_id,))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    user_reviews = []
    for row in rows:
        user_reviews.append({
            "id": row[0],
            "text": row[1],
            "rating": row[2],
            "sentiment": row[3],
            "created_at": row[4].isoformat() if row[4] else None,
            "movie_title": row[5],
            "poster_path": row[6],
            "movie_id": row[7]
        })

    return user_reviews

# =========================
# RECOMMENDATION ENGINE (AI POWERED)
# =========================

@app.get("/recommendations/{user_id}")
def get_recommendations(user_id: str):
    # Simple logging to a file
    with open("rec_log.txt", "a") as f:
        f.write(f"\n[{datetime.now()}] Rec request for user: {user_id}")

    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        return {"message": "TMDB_API_KEY missing", "movies": []}

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Get titles and ratings (Order by latest first)
        cursor.execute("""
            SELECT m.title, r.rating, r.sentiment, m.tmdb_id
            FROM reviews r
            JOIN movies m ON r.movie_id = m.id
            WHERE r.user_id = %s AND (r.is_spam = FALSE OR r.is_spam IS NULL)
            ORDER BY r.created_at DESC;
        """, (user_id,))
        reviewed_movies = cursor.fetchall()

        # Exclude TMDB IDs already reviewed
        reviewed_tmdb_ids = {str(m[3]) for m in reviewed_movies if m and m[3]}

        cursor.close()
        conn.close()
    except Exception as e:
        with open("rec_log.txt", "a") as f: f.write(f"\nDB Error: {e}")
        return {"message": "Database error occurred.", "movies": []}

    if not reviewed_movies:
        return {"message": "Review some movies first to get personalized recommendations!", "movies": []}

    # 2. Derive genres from the user's previously reviewed movies (same TMDB API).
    import time
    # Weight genres by the user's rating so "liked" movies influence recommendations more.
    genre_weight = {}

    def add_genres_from_tmdb(tmdb_id: str, rating: float):
        tmdb_movie_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
        # Retry to avoid intermittent connection resets.
        last_err = None
        for attempt in range(3):
            try:
                resp = requests.get(
                    tmdb_movie_url,
                    params={"api_key": api_key, "language": "en-US"},
                    timeout=8,
                )
                resp.raise_for_status()
                payload = resp.json()
                break
            except Exception as e:
                last_err = e
                time.sleep(0.6 * (attempt + 1))
        else:
            raise last_err

        for g in payload.get("genres", []) or []:
            gid = str(g.get("id"))
            if not gid:
                continue
            genre_weight[gid] = genre_weight.get(gid, 0) + float(rating)

    # Use only positive reviews to derive taste; if the user has no positives,
    # fall back to all non-spam reviews.
    positive_reviews = [m for m in reviewed_movies if (m[2] == "positive" or (m[1] is not None and float(m[1]) >= 4.0))]
    source_movies = positive_reviews if positive_reviews else reviewed_movies

    # Only use TMDB ids we have in the DB
    used = 0
    for (title, rating, sentiment, tmdb_id) in source_movies:
        if not tmdb_id:
            continue
        try:
            add_genres_from_tmdb(str(tmdb_id), rating)
            used += 1
        except Exception as e:
            # Keep going even if a single TMDB call fails.
            with open("rec_log.txt", "a") as f:
                f.write(f"\nTMDB movie genres error for tmdb_id={tmdb_id}: {e}")
        if used >= 4:
            break  # cap external calls per request

    if not genre_weight:
        # Reasonable default if TMDB genre fetch fails.
        genre_ids = ["28", "12"]
    else:
        sorted_genres = sorted(genre_weight.items(), key=lambda x: x[1], reverse=True)
        # Pick top 5 genres for "same or related" recommendations
        genre_ids = [gid for gid, _w in sorted_genres[:5]]

    # 2.1 Reasoning text (use genre names when possible)
    reasoning = "Based on your previous reviews, here are movies you may like."
    try:
        genre_list_url = "https://api.themoviedb.org/3/genre/movie/list"
        last_err = None
        for attempt in range(3):
            try:
                resp = requests.get(
                    genre_list_url,
                    params={"api_key": api_key, "language": "en-US"},
                    timeout=8,
                )
                resp.raise_for_status()
                genres_payload = resp.json()
                break
            except Exception as e:
                last_err = e
                time.sleep(0.6 * (attempt + 1))
        else:
            raise last_err

        id_to_name = {str(g["id"]): g.get("name") for g in (genres_payload.get("genres", []) or []) if g.get("id") is not None}

        top_names = [id_to_name.get(gid) for gid in genre_ids if id_to_name.get(gid)]
        liked_titles = [t for (t, r, _sent, _tmdb) in reviewed_movies[:4] if r is not None and float(r) >= 4.0]
        if liked_titles and top_names:
            reasoning = f"Because you enjoyed {liked_titles[0]} and similar styles: {', '.join(top_names[:3])}."
        elif top_names:
            reasoning = f"Because you tend to rate these genres highly: {', '.join(top_names[:3])}."
    except Exception:
        pass

    # 3. TMDB Discovery
    import random
    import time
    tmdb_url = "https://api.themoviedb.org/3/discover/movie"
    discovered_pages = [1]  # keep extremely low for responsiveness
    vote_count_thresholds = [20, 10]  # loosen slightly to avoid empty responses

    def tmdb_get_json(url: str, params: dict, timeout: int = 8, retries: int = 2):
        last_err = None
        for attempt in range(retries):
            try:
                r = requests.get(url, params=params, timeout=timeout)
                r.raise_for_status()
                return r.json()
            except Exception as e:
                last_err = e
                # Small backoff before retrying
                time.sleep(0.3 * (attempt + 1))
        raise last_err

    def discover(with_genres_csv, vote_count_gte: int, page: int):
        params = {
            "api_key": api_key,
            "sort_by": "popularity.desc",
            "language": "en-US",
            "page": page,
            "with_original_language": "ml",  # Malayalam-only
        }
        if vote_count_gte > 0:
            params["vote_count.gte"] = vote_count_gte
        if with_genres_csv:
            params["with_genres"] = with_genres_csv
        return tmdb_get_json(tmdb_url, params=params).get("results", [])

    # 4. Filter, upsert into DB, and format
    recommendations = []
    seen_tmdb_ids = set()

    # Re-open DB connection for upsert.
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Malayalam-only + genre-relaxation fallback:
        # Try top N genres first (N=5,4,3,2,1), then finally Malayalam-only without genre filter.
        genre_sets = [
            genre_ids[:5],
            genre_ids[:3],
            genre_ids[:2],
            genre_ids[:1],
            None,  # still Malayalam-only (no with_genres)
        ]

        for genre_list in genre_sets:
            with_genres_csv = ",".join(genre_list) if genre_list else None
            for vote_thr in vote_count_thresholds:
                for page in discovered_pages:
                    try:
                        tmdb_results = discover(with_genres_csv, vote_thr, page)
                    except Exception as e:
                        with open("rec_log.txt", "a") as f:
                            f.write(f"\nTMDB discover error (genres={with_genres_csv}, vote_thr={vote_thr}, page={page}): {e}")
                        continue

                    for m in tmdb_results:
                        tmdb_id = str(m.get("id"))
                        if not tmdb_id:
                            continue
                        if tmdb_id in reviewed_tmdb_ids or tmdb_id in seen_tmdb_ids:
                            continue

                        # Ensure the movie exists in your `movies` table.
                        cursor.execute("SELECT id FROM movies WHERE tmdb_id = %s", (tmdb_id,))
                        row = cursor.fetchone()
                        if row:
                            internal_id = row[0]
                        else:
                            cursor.execute(
                                """
                                INSERT INTO movies (tmdb_id, title, poster_path, release_date, overview, avg_rating)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                RETURNING id;
                                """,
                                (
                                    tmdb_id,
                                    m.get("title"),
                                    m.get("poster_path"),
                                    m.get("release_date"),
                                    m.get("overview"),
                                    float(m.get("vote_average") or 0.0),
                                ),
                            )
                            internal_id = cursor.fetchone()[0]
                            conn.commit()

                        recommendations.append(
                            {
                                "id": internal_id,  # IMPORTANT: frontend expects internal `movies.id`
                                "title": m.get("title"),
                                "poster_path": m.get("poster_path"),
                                "release_date": m.get("release_date"),
                                "overview": m.get("overview"),
                                "avg_rating": m.get("vote_average"),
                                "ai_reason": reasoning,
                                "tmdb_id": tmdb_id,
                            }
                        )
                        seen_tmdb_ids.add(tmdb_id)

                        if len(recommendations) >= 15:
                            break

                    if len(recommendations) >= 15:
                        break
                if len(recommendations) >= 15:
                    break
            if len(recommendations) >= 15:
                break
    finally:
        cursor.close()
        conn.close()

    with open("rec_log.txt", "a") as f:
        f.write(f"\nReturning {len(recommendations)} recommendations.")
    return recommendations[:15]
