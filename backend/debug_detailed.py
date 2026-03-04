import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def debug():
    conn = psycopg2.connect(
        host="aws-1-ap-southeast-2.pooler.supabase.com",
        database="postgres",
        user="postgres.apdzemtysvmlojlwkjxu",
        password="souravgenshin",
        port="5432",
        sslmode="require"
    )
    cursor = conn.cursor()

    # 1. Look for the movie with avg_rating = 0.8
    print("--- Searching for movies with avg_rating = 0.8 ---")
    cursor.execute("SELECT id, title, avg_rating FROM movies WHERE avg_rating = 0.8")
    movies = cursor.fetchall()
    
    for m_id, title, avg in movies:
        print(f"\nMOVIE: {title} (ID: {m_id})")
        print(f"Reported Avg Rating: {avg}")
        
        # 2. Check ALL reviews for this movie
        cursor.execute("SELECT id, rating, review_text, created_at FROM reviews WHERE movie_id = %s", (m_id,))
        reviews = cursor.fetchall()
        print(f"TOTAL REVIEWS FOUND: {len(reviews)}")
        
        sum_ratings = 0
        for r_id, r_rating, r_text, r_date in reviews:
            print(f"  - Review [{r_id}]: Rating={r_rating}, Date={r_date}")
            print(f"    Text: {r_text[:100]}...")
            sum_ratings += r_rating
        
        if len(reviews) > 0:
            calc_avg = sum_ratings / len(reviews)
            print(f"CALCULATED AVG: {calc_avg}")
            if calc_avg != avg:
                print("!!! MISMATCH DETECTED between calc_avg and avg_rating column !!!")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    debug()
