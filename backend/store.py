import json
import os
import psycopg2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel

from model import analyze

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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


@app.post("/analyze-review")
def analyze_review(data: ReviewRequest):

    result = analyze(data.review)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO reviews (movie_id, review_text, rating, sentiment, aspects)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
    """, (
        data.movie_id,
        data.review,
        result["rating"],
        result["sentiment"],
        json.dumps(result["aspects"])
    ))

    review_id = cursor.fetchone()[0]

    # Update movie average rating
    cursor.execute("""
        UPDATE movies
        SET avg_rating = (
            SELECT COALESCE(AVG(rating), 0)
            FROM reviews
            WHERE movie_id = %s
        )
        WHERE id = %s;
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

    # Default structure
    aggregated = {
        "acting": [],
        "story": [],
        "bgm": [],
        "direction": [],
        "visuals": []
    }

    for row in rows:
        aspects = row[0]
        if aspects:
            for key in aggregated:
                value = aspects.get(key)
                if value is not None:
                    aggregated[key].append(value)

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
    movies = [dict(zip(columns, row)) for row in rows]

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