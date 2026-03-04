import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def find_review():
    conn = psycopg2.connect(
        host="aws-1-ap-southeast-2.pooler.supabase.com",
        database="postgres",
        user="postgres.apdzemtysvmlojlwkjxu",
        password="souravgenshin",
        port="5432",
        sslmode="require"
    )
    cursor = conn.cursor()

    print("Looking for reviews with rating between 2.3 and 2.5...")
    cursor.execute("SELECT movie_id, rating, review_text, id FROM reviews WHERE rating >= 2.3 AND rating <= 2.5")
    rows = cursor.fetchall()
    
    for m_id, rating, text, r_id in rows:
        print(f"\nFOUND REVIEW: {r_id}")
        print(f"Movie ID: {m_id}")
        print(f"Rating: {rating}")
        print(f"Text: {text}")
        
        # Check parent movie
        cursor.execute("SELECT title, avg_rating FROM movies WHERE id = %s", (m_id,))
        movie = cursor.fetchone()
        if movie:
            print(f"MOVIE TITLE: {movie[0]}")
            print(f"MOVIE AVG_RATING: {movie[1]}")
            
            # Count ALL reviews for this movie
            cursor.execute("SELECT rating, id FROM reviews WHERE movie_id = %s", (m_id,))
            all_revs = cursor.fetchall()
            print(f"ALL REVIEWS FOR THIS MOVIE: {all_revs}")
            if len(all_revs) > 0:
                print(f"Calculated Avg: {sum(r[0] for r in all_revs)/len(all_revs)}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    find_review()
