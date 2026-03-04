import psycopg2
import os
import json
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

def check_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        print("--- Review Counts by User ---")
        cur.execute("SELECT user_id, user_name, count(1) FROM reviews GROUP BY user_id, user_name")
        rows = cur.fetchall()
        for row in rows:
            print(f"ID: {row[0]} | Name: {row[1]} | Count: {row[2]}")
            
        print("\n--- 'abhishek s' Specific Check ---")
        cur.execute("SELECT r.user_id, r.user_name, r.movie_id, m.title, m.tmdb_id FROM reviews r LEFT JOIN movies m ON r.movie_id = m.id WHERE r.user_name ILIKE '%abhishek%'")
        rows = cur.fetchall()
        if not rows:
            print("No reviews found for name 'abhishek'")
        for row in rows:
            print(f"User ID: {row[0]} | Name: {row[1]} | Movie internal ID: {row[2]} | Movie Title: {row[3]} | Movie TMDB ID: {row[4]}")
            
        print("\n--- GEMINI CHECK ---")
        key = os.getenv("GEMINI_API_KEY")
        print(f"GEMINI_API_KEY exists: {bool(key)}")
        if key:
            print(f"Key starts with: {key[:5]}...")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB Error: {e}")

if __name__ == "__main__":
    check_db()
