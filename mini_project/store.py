import os
import requests
import psycopg2
from datetime import date
from fastapi import FastAPI
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()

START_DATE = "2026-02-25"   # Only movies after this date

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


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

    response = requests.get(url, params=params)

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

    if inserted_count > 0:
        print(f"{inserted_count} new movies inserted.")
    else:
        print("No new movies to insert.")


@app.get("/sync")
def manual_sync():
    sync_new_releases()
    return {"message": "Sync completed"}


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