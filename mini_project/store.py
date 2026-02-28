import os
import requests
import psycopg2
from datetime import date
from fastapi import FastAPI
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date, timedelta

# Load environment variables
load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
print("TMDB KEY:", TMDB_API_KEY)

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT")
}

app = FastAPI()

# --------------------------------------------------
# Database Connection Function
# --------------------------------------------------

import os

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# --------------------------------------------------
# Sync Function (Runs Daily at 10 AM)
# --------------------------------------------------

def sync_today_movies():

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
    data = response.json()

    

    if response.status_code != 200:
        print("TMDB Error:", response.status_code, response.text)
        return

    data = response.json()

    results = data.get("results", [])

    if not results:
        print("No Malayalam movies found for today.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    inserted_count = 0

    for movie in data["results"]:

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

# --------------------------------------------------
# Manual Trigger Endpoint (Optional)
# --------------------------------------------------

@app.get("/sync")
def manual_sync():
    sync_today_movies()
    return {"message": "Sync completed"}

# --------------------------------------------------
# Scheduler Setup (10:00 AM Daily)
# --------------------------------------------------

scheduler = BackgroundScheduler()

scheduler.add_job(
    sync_today_movies,
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