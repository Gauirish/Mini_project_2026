import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def check_schema():
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
        cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'movies';")
        columns = cursor.fetchall()
        print("Movies table columns:")
        for col in columns:
            print(f" - {col[0]}: {col[1]}")
    except Exception as e:
        print(f"Error checking schema: {e}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_schema()
