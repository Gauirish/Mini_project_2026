import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def add_column():
    conn = psycopg2.connect(
        host="aws-1-ap-southeast-2.pooler.supabase.com",
        database="postgres",
        user="postgres.apdzemtysvmlojlwkjxu",
        password="souravgenshin",
        port="5432",
        sslmode="require"
    )
    conn.autocommit = True
    cursor = conn.cursor()

    print("Attempting to add 'genres' column to 'movies' table...")
    try:
        cursor.execute("ALTER TABLE movies ADD COLUMN IF NOT EXISTS genres JSONB;")
        print("Successfully added 'genres' column!")
    except Exception as e:
        print(f"Error adding column: {e}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    add_column()
