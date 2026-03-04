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

def backfill():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Ensure column exists
    print("Ensuring 'genres' column exists...")
    cursor.execute("ALTER TABLE movies ADD COLUMN IF NOT EXISTS genres JSONB")
    conn.commit()

    # Get movies with NULL genres
    cursor.execute("SELECT id, tmdb_id, title FROM movies WHERE genres IS NULL")
    movies = cursor.fetchall()
    
    if not movies:
        print("No movies need backfilling.")
        return

    api_key = os.getenv("TMDB_API_KEY")
    updated_count = 0

    for m_id, tmdb_id, title in movies:
        print(f"Fetching genres for: {title} ({tmdb_id})")
        tmdb_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
        params = {"api_key": api_key}
        
        try:
            response = requests.get(tmdb_url, params=params)
            response.raise_for_status()
            data = response.json()
            genre_ids = [g["id"] for g in data.get("genres", [])]
            
            cursor.execute("UPDATE movies SET genres = %s WHERE id = %s", (json.dumps(genre_ids), m_id))
            updated_count += 1
            print(f"Updated {title} with genres: {genre_ids}")
        except Exception as e:
            print(f"Error updating {title}: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Successfully updated {updated_count} movies.")

if __name__ == "__main__":
    backfill()
