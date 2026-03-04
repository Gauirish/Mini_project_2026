import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def get_db_connection():
    # Credentials from store.py
    return psycopg2.connect(
        host="aws-1-ap-southeast-2.pooler.supabase.com",
        database="postgres",
        user="postgres.apdzemtysvmlojlwkjxu",
        password="souravgenshin",
        port="5432",
        sslmode="require"
    )

def count_movies():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM movies;")
        count = cursor.fetchone()[0]
        
        print(f"\n========================================")
        print(f"       SUPABASE MOVIE REPORT            ")
        print(f"========================================")
        print(f" Total movies in database: {count}")
        print(f"========================================\n")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    count_movies()
