import os
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse


DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

# Parse the DATABASE_URL to get connection params
url = urlparse(DATABASE_URL)
DB_NAME = url.path[1:]
DB_USER = url.username
DB_PASSWORD = url.password
DB_HOST = url.hostname
DB_PORT = url.port


def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        cursor_factory=RealDictCursor
    )


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            date DATE NOT NULL,
            location TEXT NOT NULL,
            description TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


# Auto-create table when this file is imported
try:
    init_db()
    print("✅ Database initialized successfully.")
except Exception as e:
    print("⚠️ Error initializing database:", e)
