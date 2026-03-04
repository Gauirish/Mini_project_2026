import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def update_schema():
    conn = psycopg2.connect(
        host="aws-1-ap-southeast-2.pooler.supabase.com",
        database="postgres",
        user="postgres.apdzemtysvmlojlwkjxu",
        password="souravgenshin",
        port="5432",
        sslmode="require"
    )
    cursor = conn.cursor()

    print("Updating 'reviews' table to include user identification...")
    
    # 1. Add user_id column (linking to auth.users if we use Supabase DB directly, 
    # but for simplicity and since we manage auth in frontend, we'll store user_id as text)
    # 2. Add user_name column for quick display
    
    try:
        cursor.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS user_id TEXT;")
        cursor.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS user_name TEXT;")
        conn.commit()
        print("Schema updated successfully!")
    except Exception as e:
        print(f"Error updating schema: {e}")
        conn.rollback()

    cursor.close()
    conn.close()

if __name__ == "__main__":
    update_schema()
