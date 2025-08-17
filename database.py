import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# ---------------- USERS ----------------
def init_users_table():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            conn.commit()

def add_user(username, password):
    init_users_table()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (username, password)
            )
            conn.commit()

def get_user(username):
    init_users_table()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE username=%s", (username,))
            return cur.fetchone()


# ---------------- EVENTS ----------------
def add_event(user_id, name, date, location, description=None):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO events (user_id, name, date, location, description) VALUES (%s, %s, %s, %s, %s)",
                (user_id, name, date, location, description)
            )
            conn.commit()

def get_all_events(user_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM events WHERE user_id=%s ORDER BY date",
                (user_id,)
            )
            return cur.fetchall()

def update_event(event_id, name, date, location, description=None):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE events SET name=%s, date=%s, location=%s, description=%s WHERE id=%s",
                (name, date, location, description, event_id)
            )
            conn.commit()

def delete_event(event_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM events WHERE id=%s", (event_id,))
            conn.commit()


# ---------------- SUB-EVENTS ----------------
def add_sub_event(event_id, name, contact=None, num_participants=None, participants=None, teacher_in_charge=None):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO sub_events
                (event_id, name, contact, num_participants, participants, teacher_in_charge)
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (event_id, name, contact, num_participants, participants, teacher_in_charge)
            )
            conn.commit()

def get_sub_events(event_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT * FROM sub_events WHERE event_id=%s ORDER BY id""",
                (event_id,)
            )
            return cur.fetchall()

def update_sub_event(sub_event_id, name, contact=None, num_participants=None, participants=None, teacher_in_charge=None):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE sub_events
                   SET name=%s, contact=%s, num_participants=%s, participants=%s, teacher_in_charge=%s
                   WHERE id=%s""",
                (name, contact, num_participants, participants, teacher_in_charge, sub_event_id)
            )
            conn.commit()

def delete_sub_event(sub_event_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM sub_events WHERE id=%s", (sub_event_id,))
            conn.commit()


# ---------------- INITIALIZATION ----------------
def init_db():
    init_users_table()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id SERIAL PRIMARY KEY,
                    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    date DATE NOT NULL,
                    location TEXT NOT NULL,
                    description TEXT
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sub_events (
                    id SERIAL PRIMARY KEY,
                    event_id INT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    contact TEXT,
                    num_participants INT,
                    participants TEXT,
                    teacher_in_charge TEXT
                )
            """)
            conn.commit()
    print("✅ PostgreSQL DB initialized successfully")
