import os
import psycopg2
import psycopg2.extras
from urllib.parse import urlparse

# ---------------- DATABASE CONNECTION ----------------
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise Exception("DATABASE_URL not set in environment variables.")

url = urlparse(DATABASE_URL)
DB_PARAMS = {
    'host': url.hostname,
    'port': url.port or 5432,
    'dbname': url.path[1:],  # remove leading '/'
    'user': url.username,
    'password': url.password
}

def get_connection():
    return psycopg2.connect(**DB_PARAMS)

# ---------------- USERS ----------------
def create_user(username, password):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id",
            (username, password)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        return user_id
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return None
    finally:
        cur.close()
        conn.close()

def authenticate_user(username, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM users WHERE username=%s AND password=%s",
        (username, password)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else None

# ---------------- EVENTS ----------------
def get_all_events(user_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(
        "SELECT * FROM events WHERE user_id=%s ORDER BY date",
        (user_id,)
    )
    events = cur.fetchall()
    cur.close()
    conn.close()
    return events

def add_event(user_id, name, date, location, description):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO events (user_id, name, date, location, description) VALUES (%s,%s,%s,%s,%s)",
        (user_id, name, date, location, description)
    )
    conn.commit()
    cur.close()
    conn.close()

def edit_event(event_id, name, date, location, description):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE events SET name=%s, date=%s, location=%s, description=%s WHERE id=%s",
        (name, date, location, description, event_id)
    )
    conn.commit()
    cur.close()
    conn.close()

def delete_event(event_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM events WHERE id=%s", (event_id,))
    conn.commit()
    cur.close()
    conn.close()

# ---------------- SUB-EVENTS ----------------
def get_sub_events(event_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM sub_events WHERE event_id=%s ORDER BY id", (event_id,))
    subs = cur.fetchall()
    cur.close()
    conn.close()
    return subs

def add_sub_event(event_id, name, contact, num_participants, participants, teacher):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sub_events (event_id,name,contact,num_participants,participants,teacher) "
        "VALUES (%s,%s,%s,%s,%s,%s)",
        (event_id, name, contact, num_participants, participants, teacher)
    )
    conn.commit()
    cur.close()
    conn.close()

def edit_sub_event(sub_id, event_id, name, contact, num_participants, participants, teacher):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE sub_events SET event_id=%s, name=%s, contact=%s, num_participants=%s, participants=%s, teacher=%s "
        "WHERE id=%s",
        (event_id, name, contact, num_participants, participants, teacher, sub_id)
    )
    conn.commit()
    cur.close()
    conn.close()

def delete_sub_event(sub_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM sub_events WHERE id=%s", (sub_id,))
    conn.commit()
    cur.close()
    conn.close()

# ---------------- INIT TABLES ----------------
def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            date DATE NOT NULL,
            location TEXT NOT NULL,
            description TEXT
        )
    """)

    # Check if user_id exists, add if missing
    cur.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='events' AND column_name='user_id'
            ) THEN
                ALTER TABLE events ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;
            END IF;
        END
        $$;
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sub_events (
            id SERIAL PRIMARY KEY,
            event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            contact TEXT,
            num_participants INTEGER,
            participants TEXT,
            teacher TEXT
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    create_tables()
