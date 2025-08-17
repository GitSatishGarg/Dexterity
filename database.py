import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


# ----------------- INITIALIZATION -----------------
def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Users table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            # Events table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id SERIAL PRIMARY KEY,
                    username TEXT NOT NULL REFERENCES users(username) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    date DATE NOT NULL,
                    location TEXT NOT NULL,
                    description TEXT
                )
            """)
            # Sub-events table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sub_events (
                    id SERIAL PRIMARY KEY,
                    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    contact TEXT,
                    num_participants INTEGER,
                    participants TEXT,
                    teacher_in_charge TEXT
                )
            """)
    print("✅ Database initialized successfully.")


# ----------------- USERS -----------------
def add_user(username, password):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, password)
            )

def get_user(username):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, username, password FROM users WHERE username=%s", (username,))
            return cur.fetchone()


# ----------------- EVENTS -----------------
def add_event(username, name, date, location, description):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO events (username, name, date, location, description) VALUES (%s, %s, %s, %s, %s)",
                (username, name, date, location, description)
            )

def get_all_events(username):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, date, location, description FROM events WHERE username=%s ORDER BY date",
                (username,)
            )
            return cur.fetchall()

def update_event(event_id, name, date, location, description):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE events SET name=%s, date=%s, location=%s, description=%s WHERE id=%s",
                (name, date, location, description, event_id)
            )

def delete_event(event_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM events WHERE id=%s", (event_id,))


# ----------------- SUB-EVENTS -----------------
def add_sub_event(event_id, name, contact, num_participants, participants, teacher_in_charge):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO sub_events
                   (event_id, name, contact, num_participants, participants, teacher_in_charge)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (event_id, name, contact, num_participants, participants, teacher_in_charge)
            )

def get_sub_events(event_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id, name, contact, num_participants, participants, teacher_in_charge
                   FROM sub_events WHERE event_id=%s""",
                (event_id,)
            )
            return cur.fetchall()

def update_sub_event(sub_id, name, contact, num_participants, participants, teacher_in_charge):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE sub_events
                   SET name=%s, contact=%s, num_participants=%s, participants=%s, teacher_in_charge=%s
                   WHERE id=%s""",
                (name, contact, num_participants, participants, teacher_in_charge, sub_id)
            )

def delete_sub_event(sub_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM sub_events WHERE id=%s", (sub_id,))
