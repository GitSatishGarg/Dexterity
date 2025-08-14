import os
import psycopg2
from psycopg.rows import dict_row

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

def get_db_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


# ---------- INIT DB ----------
def init_db():
    """
    Creates the 'events' table if it doesn't exist.
    """
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


# ---------- CRUD FUNCTIONS ----------
def get_events():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM events ORDER BY date")
    events = cur.fetchall()
    cur.close()
    conn.close()
    return events


def add_event(name, date, location, description=None):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO events (name, date, location, description) VALUES (%s, %s, %s, %s)",
        (name, date, location, description)
    )
    conn.commit()
    cur.close()
    conn.close()


def delete_event(event_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM events WHERE id=%s", (event_id,))
    conn.commit()
    cur.close()
    conn.close()


# ---------- Optional: initialize on import ----------
try:
    init_db()
    print("✅ Database initialized successfully.")
except Exception as e:
    print("⚠️ Error initializing database:", e)
