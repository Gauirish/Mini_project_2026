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

# =========================
# DATABASE CONNECTION
# =========================

def get_db_connection():
    return psycopg2.connect(
        host="aws-1-ap-southeast-2.pooler.supabase.com",
        database="postgres",
        user="postgres.apdzemtysvmlojlwkjxu",
        password="souravgenshin",
        port="5432",
        sslmode="require"
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

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert review
    cursor.execute("""
        INSERT INTO reviews (movie_id, review_text, rating, sentiment, aspects, user_id, user_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """, (
        data.movie_id,
        data.review,
        result["rating"],
        result["sentiment"],
        json.dumps(result["aspects"]),
        data.user_id,
        data.user_name
    ))

    review_id = cursor.fetchone()[0]

    # Update movie average rating
    cursor.execute("""
        UPDATE movies
        SET avg_rating = (
            SELECT COALESCE(AVG(rating),0)
            FROM reviews
            WHERE movie_id=%s
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
        "aspects": result["aspects"]
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
        WHERE movie_id = %s
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
        WHERE movie_id = %s
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
        "primary_release_date.gte": today,
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
            INSERT INTO movies (tmdb_id, title, poster_path, release_date, overview, avg_rating, genres)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (str(tmdb_id), title, poster_path, release_date, overview, 0, json.dumps(genre_ids)))
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
    import google.generativeai as genai
    
    # Simple logging to a file
    with open("rec_log.txt", "a") as f:
        f.write(f"\n[{datetime.now()}] Rec request for user: {user_id}")

    gemini_key = os.getenv("GEMINI_API_KEY")
    api_key = os.getenv("TMDB_API_KEY")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Get titles and ratings (Order by latest first)
        cursor.execute("""
            SELECT m.title, r.rating, m.tmdb_id
            FROM reviews r
            JOIN movies m ON r.movie_id = m.id
            WHERE r.user_id = %s
            ORDER BY r.created_at DESC;
        """, (user_id,))
        reviewed_movies = cursor.fetchall()

        # Get IDs already reviewed
        cursor.execute("SELECT movie_id FROM reviews WHERE user_id = %s", (user_id,))
        reviewed_movie_ids = {str(row[0]) for row in cursor.fetchall()}
        # Also include TMDB IDs in the reviewed set
        reviewed_tmdb_ids = {str(m[2]) for m in reviewed_movies if m[2]}

        cursor.close()
        conn.close()
    except Exception as e:
        with open("rec_log.txt", "a") as f: f.write(f"\nDB Error: {e}")
        return {"message": "Database error occurred.", "movies": []}

    if not reviewed_movies:
        return {"message": "Review some movies first to get personalized recommendations!", "movies": []}

    # 2. Taste Analysis
    movie_list_str = ", ".join([f"{m[0]}" for m in reviewed_movies])
    keywords = ""
    reasoning = "Based on your interest in " + ", ".join([m[0] for m in reviewed_movies[:2]])
    
    if gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""
            User has reviewed: {movie_list_str}.
            Analyze their taste. Provide:
            1. A comma-separated list of 5-8 TMDB genre IDs or keywords.
            2. A one-sentence explanation (reasoning).
            Format:
            KEYWORDS: [ids/keywords]
            EXPLANATION: [sentence]
            """
            response = model.generate_content(prompt)
            text = response.text
            with open("rec_log.txt", "a") as f: f.write(f"\nGemini response: {text[:100]}")
            
            if "KEYWORDS:" in text:
                k_part = text.split("KEYWORDS:")[1].split("EXPLANATION:")[0]
                keywords = k_part.strip().replace("[", "").replace("]", "")
            if "EXPLANATION:" in text:
                reasoning = text.split("EXPLANATION:")[1].strip().replace("[", "").replace("]", "")
        except Exception as e:
            with open("rec_log.txt", "a") as f: f.write(f"\nGemini Error: {e}")

    # 2.5 - Hard Fallback if Gemini failed or is missing
    if not keywords:
        # Simple mapping-based genre extraction if DB column failed
        # Common Action/Sci-Fi/Drama mapped based on typical titles (Simulated AI)
        all_reviewed_titles = " ".join([m[0].lower() for m in reviewed_movies])
        detected_genres = []
        if any(w in all_reviewed_titles for w in ["action", "hero", "war", "fight", "man", "avenger"]): detected_genres.append("28") # Action
        if any(w in all_reviewed_titles for w in ["love", "romance", "heart", "story"]): detected_genres.append("10749") # Romance
        if any(w in all_reviewed_titles for w in ["scary", "horror", "ghost", "dead"]): detected_genres.append("27") # Horror
        if any(w in all_reviewed_titles for w in ["space", "future", "alien", "tech"]): detected_genres.append("878") # Sci-Fi
        if any(w in all_reviewed_titles for w in ["laugh", "comedy", "funny", "joke"]): detected_genres.append("35") # Comedy
        
        keywords = ",".join(detected_genres) if detected_genres else "28,12" # Default to Action/Adventure
        reasoning = f"Based on your interest in {reviewed_movies[0][0]} and similar stories."

    # 3. TMDB Discovery
    import random
    tmdb_url = "https://api.themoviedb.org/3/discover/movie"
    # Basic params - Add random page for freshness
    random_page = random.randint(1, 3) 
    params = {
        "api_key": api_key,
        "sort_by": "popularity.desc",
        "language": "en-US",
        "page": random_page,
        "vote_count.gte": 80 # Lowered slightly for more variety
    }

    if keywords:
        # Check if IDs or text
        parts = [p.strip() for p in keywords.split(",")]
        ids = [p for p in parts if p.isdigit()]
        if ids:
            params["with_genres"] = ",".join(ids)
        else:
            params["with_keywords"] = keywords

    try:
        response = requests.get(tmdb_url, params=params)
        response.raise_for_status()
        tmdb_results = response.json().get("results", [])
    except Exception as e:
        with open("rec_log.txt", "a") as f: f.write(f"\nTMDB Error: {e}")
        return {"message": "Failed to fetch from TMDB.", "movies": []}

    # 4. Filter and Format
    recommendations = []
    for m in tmdb_results:
        tmdb_id = str(m.get("id"))
        # Exclude if already reviewed (by TMDB ID or internal ID)
        if tmdb_id in reviewed_tmdb_ids or tmdb_id in reviewed_movie_ids:
            continue
            
        recommendations.append({
            "id": tmdb_id,
            "title": m.get("title"),
            "poster_path": m.get("poster_path"),
            "release_date": m.get("release_date"),
            "overview": m.get("overview"),
            "avg_rating": m.get("vote_average"),
            "ai_reason": reasoning
        })

    with open("rec_log.txt", "a") as f: f.write(f"\nReturning {len(recommendations)} recommendations.")
    return recommendations[:15]
