import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def cleanup():
    conn = psycopg2.connect(
        host="aws-1-ap-southeast-2.pooler.supabase.com",
        database="postgres",
        user="postgres.apdzemtysvmlojlwkjxu",
        password="souravgenshin",
        port="5432",
        sslmode="require"
    )
    cursor = conn.cursor()

    print("Identifying movies with 0.0 reviews...")
    # Find movie_ids that have reviews with rating = 0
    cursor.execute("SELECT DISTINCT movie_id FROM reviews WHERE rating = 0")
    movie_ids = [row[0] for row in cursor.fetchall()]

    if not movie_ids:
        print("No stale 0.0 reviews found.")
        return

    print(f"Cleaning up {len(movie_ids)} affected movies...")

    for m_id in movie_ids:
        # Delete the 0.0 reviews
        cursor.execute("DELETE FROM reviews WHERE movie_id = %s AND rating = 0", (m_id,))
        deleted_count = cursor.rowcount
        print(f"Movie {m_id}: Deleted {deleted_count} stale review(s).")

        # Recalculate average
        cursor.execute("""
            UPDATE movies
            SET avg_rating = (
                SELECT COALESCE(AVG(rating), 0)
                FROM reviews
                WHERE movie_id = %s
            )
            WHERE id = %s
        """, (m_id, m_id))

    conn.commit()
    print("\nDatabase cleanup complete!")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    cleanup()
