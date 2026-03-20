import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def count_movies():
    conn = psycopg2.connect(
        host="aws-1-ap-southeast-2.pooler.supabase.com",
        database="postgres",
        user="postgres.apdzemtysvmlojlwkjxu",
        password="souravgenshin",
        port="5432",
        sslmode="require"
    )
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT count(*) FROM movies;")
        count = cursor.fetchone()[0]
        print(f"Total movies in database: {count}")
    except Exception as e:
        print(f"Error counting movies: {e}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    count_movies()
