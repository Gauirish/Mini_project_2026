import os
import json
import psycopg2
import requests
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        host="aws-1-ap-southeast-2.pooler.supabase.com",
        database="postgres",
        user="postgres.apdzemtysvmlojlwkjxu",
        password="souravgenshin",
        port="5432",
        sslmode="require"
    )

def test_recommendations(user_id):
    print(f"Testing recommendations for user_id: {user_id}")
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Get titles and ratings
    cursor.execute("""
        SELECT m.title, r.rating, m.tmdb_id
        FROM reviews r
        JOIN movies m ON r.movie_id = m.id
        WHERE r.user_id = %s;
    """, (user_id,))
    
    reviewed_movies = cursor.fetchall()
    print(f"Found {len(reviewed_movies)} reviewed movies.")
    for m in reviewed_movies:
        print(f" - {m[0]} ({m[1]}/5)")

    cursor.close()
    conn.close()

    if not reviewed_movies:
        print("No reviewed movies found. Returning.")
        return

    # 2. TMDB Discovery
    api_key = os.getenv("TMDB_API_KEY")
    print(f"TMDB_API_KEY exists: {bool(api_key)}")
    
    tmdb_url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": api_key,
        "sort_by": "popularity.desc",
        "language": "en-US",
        "page": 1,
        "vote_count.gte": 150
    }

    try:
        response = requests.get(tmdb_url, params=params)
        print(f"TMDB Response Status: {response.status_code}")
        data = response.json()
        tmdb_results = data.get("results", [])
        print(f"TMDB returned {len(tmdb_results)} results.")
        if tmdb_results:
            print(f"First result: {tmdb_results[0].get('title')}")
    except Exception as e:
        print(f"TMDB Error: {e}")

if __name__ == "__main__":
    # Use the full ID from diagnostic: b47813ac-7a7e-49ba-aacd-a12def80e03e (guessing the end or I'll query it first)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM reviews WHERE user_name = 'abhishek s' LIMIT 1")
    user_id = cur.fetchone()[0]
    cur.close()
    conn.close()
    
    test_recommendations(user_id)
