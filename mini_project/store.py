import os
import requests
import psycopg2
from datetime import date
from fastapi import FastAPI
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()

# --------------------------------------------------
# Database Connection
# --------------------------------------------------

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# --------------------------------------------------
# Sync Function
# Inserts all released Malayalam movies (<= today)
# Skips duplicates automatically
# --------------------------------------------------

def sync_released_movies():

    today = date.today().isoformat()
    url = "https://api.themoviedb.org/3/discover/movie"

    page = 1
    inserted_count = 0

    conn = get_db_connection()
    cursor = conn.cursor()

    while True:

        params = {
            "api_key": TMDB_API_KEY,
            "with_original_language": "ml",
            "primary_release_date.lte": today,
            "sort_by": "primary_release_date.desc",
            "page": page
        }

        response = requests.get(url, params=params)

        if response.status_code != 200:
            print("TMDB Error:", response.status_code, response.text)
            break

        data = response.json()
        results = data.get("results", [])

        if not results:
            break

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

        page += 1

        if page > data.get("total_pages", 1):
            break

    conn.commit()
    cursor.close()
    conn.close()

    print(f"{inserted_count} movies inserted.")

# --------------------------------------------------
# Manual Sync Endpoint
# --------------------------------------------------

@app.get("/sync")
def manual_sync():
    sync_released_movies()
    return {"message": "Sync completed"}

# --------------------------------------------------
# Scheduler (10 AM IST)
# --------------------------------------------------

scheduler = BackgroundScheduler(timezone="Asia/Kolkata")

scheduler.add_job(
    sync_released_movies,
    trigger="cron",
    hour=10,
    minute=0
)

scheduler.start()

# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/")
def root():
    return {"status": "Backend running"}