import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def check_ratings():
    conn = psycopg2.connect(
        host="aws-1-ap-southeast-2.pooler.supabase.com",
        database="postgres",
        user="postgres.apdzemtysvmlojlwkjxu",
        password="souravgenshin",
        port="5432",
        sslmode="require"
    )
    cursor = conn.cursor()

    # Find a movie with rating 0.8
    cursor.execute("SELECT id, title, avg_rating FROM movies WHERE avg_rating = 0.8 LIMIT 5")
    movies = cursor.fetchall()
    
    if not movies:
        print("No movie with 0.8 rating found. Checking for all with avg_rating > 0")
        cursor.execute("SELECT id, title, avg_rating FROM movies WHERE avg_rating > 0 LIMIT 10")
        movies = cursor.fetchall()

    for m_id, title, avg in movies:
        print(f"\nMovie: {title} (ID: {m_id}), Current Avg: {avg}")
        cursor.execute("SELECT id, rating FROM reviews WHERE movie_id = %s", (m_id,))
        rows = cursor.fetchall()
        print(f"Reviews in DB for this movie: {rows}")
        actual_avg = sum(r[1] for r in rows) / len(rows) if rows else 0
        print(f"Calculated average from reviews: {actual_avg}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_ratings()
