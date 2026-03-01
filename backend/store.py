import os
import requests
import psycopg2
from datetime import date
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

app = FastAPI()

# ✅ Enable CORS (VERY IMPORTANT for React frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

START_DATE = "2026-01-01"


# ✅ Database Connection
def get_db_connection():
    return psycopg2.connect(
        host="aws-1-ap-southeast-2.pooler.supabase.com",
        database="postgres",
        user="postgres.apdzemtysvmlojlwkjxu",
        password="souravgenshin",
        port="5432",
        sslmode="require"
    )


# ✅ Fetch and Insert Movies from TMDB
def sync_new_releases():

    today = date.today().isoformat()

    url = "https://api.themoviedb.org/3/discover/movie"

    params = {
        "api_key": TMDB_API_KEY,
        "with_original_language": "ml",
        "primary_release_date.gte": START_DATE,
        "primary_release_date.lte": today,
        "sort_by": "primary_release_date.desc",
        "page": 1
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, params=params, headers=headers, timeout=10)

    if response.status_code != 200:
        print("TMDB Error:", response.status_code, response.text)
        return

    data = response.json()
    results = data.get("results", [])

    if not results:
        print("No new Malayalam releases found.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    inserted_count = 0

    for movie in results:
        cursor.execute("""
            INSERT INTO movies (tmdb_id, title, poster_path, release_date, overview)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (tmdb_id) DO NOTHING;
        """, (
            movie["id"],
            movie["title"],
            movie.get("poster_path"),
            movie.get("release_date"),
            movie.get("overview")
        ))

        if cursor.rowcount > 0:
            inserted_count += 1

    conn.commit()
    cursor.close()
    conn.close()

    print(f"{inserted_count} new movies inserted.")


# ✅ Manual Sync Endpoint
@app.get("/sync")
def manual_sync():
    sync_new_releases()
    return {"message": "Sync completed"}


# ✅ NEW: Get All Movies (For Frontend)
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


# ✅ Scheduler (Daily 10 AM)
scheduler = BackgroundScheduler(timezone="Asia/Kolkata")

scheduler.add_job(
    sync_new_releases,
    trigger="cron",
    hour=10,
    minute=0
)

scheduler.start()


@app.get("/")
def root():
    return {"status": "Backend running"}