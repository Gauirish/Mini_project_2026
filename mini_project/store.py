import os
import requests
import psycopg2
from datetime import date, timedelta
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
# Runs daily and checks only yesterday → today releases
# --------------------------------------------------

def sync_new_releases():

    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    url = "https://api.themoviedb.org/3/discover/movie"

    params = {
        "api_key": TMDB_API_KEY,
        "with_original_language": "ml",
        "primary_release_date.gte": yesterday,
        "primary_release_date.lte": today,
        "sort_by": "primary_release_date.desc",
        "page": 1
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("TMDB Error:", response.status_code, response.text)
        return

    data = response.json()
    results = data.get("results", [])

    if not results:
        print("No new Malayalam releases today.")
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

    if inserted_count > 0:
        print(f"{inserted_count} new movies inserted.")
    else:
        print("Movies already exist. No new inserts.")

# --------------------------------------------------
# Manual Trigger Endpoint
# --------------------------------------------------

@app.get("/sync")
def manual_sync():
    sync_new_releases()
    return {"message": "Sync completed"}

# --------------------------------------------------
# Scheduler - Runs every day at 10 AM IST
# --------------------------------------------------

scheduler = BackgroundScheduler(timezone="Asia/Kolkata")

scheduler.add_job(
    sync_new_releases,
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