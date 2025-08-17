import os
import psycopg2  # type: ignore
from psycopg2.extras import RealDictCursor  # type: ignore

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")


def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


# ---------------- USERS TABLE ----------------
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


# ---------------- EVENTS TABLE ----------------
def init_events_tables():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Main events table
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
            conn.commit()


# ---------------- USERS ----------------
def add_user(username, password):
    init_users_table()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, password)
            )
            conn.commit()


def get_user(username):
    init_users_table()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, username, password FROM users WHERE username=%s", (username,))
            return cur.fetchone()


# ---------------- EVENTS ----------------
def add_event(username, name, date, location, description):
    init_events_tables()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO events (username, name, date, location, description) VALUES (%s, %s, %s, %s, %s)",
                (username, name, date, location, description)
            )
            conn.commit()


def get_all_events(username):
    init_events_tables()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, date, location, description FROM events WHERE username=%s ORDER BY date",
                (username,)
            )
            rows = cur.fetchall()
    return [
        {"id": r["id"], "name": r["name"], "date": r["date"].isoformat(), "location": r["location"], "description": r["description"]}
        for r in rows
    ]


def update_event(username, event_id, name, date, location, description):
    init_events_tables()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE events SET name=%s, date=%s, location=%s, description=%s WHERE id=%s AND username=%s",
                (name, date, location, description, event_id, username)
            )
            conn.commit()


def delete_event(username, event_id):
    init_events_tables()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM events WHERE id=%s AND username=%s",
                (event_id, username)
            )
            conn.commit()


# ---------------- SUB-EVENTS ----------------
def add_sub_event(username, event_id, name, contact, num_participants, participants, teacher_in_charge):
    init_events_tables()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO sub_events
                   (event_id, name, contact, num_participants, participants, teacher_in_charge)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (event_id, name, contact, num_participants, participants, teacher_in_charge)
            )
            conn.commit()


def get_sub_events(username, event_id):
    init_events_tables()
    # Ensure event belongs to username
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT se.id, se.name, se.contact, se.num_participants, se.participants, se.teacher_in_charge
                   FROM sub_events se
                   JOIN events e ON se.event_id = e.id
                   WHERE e.id=%s AND e.username=%s""",
                (event_id, username)
            )
            rows = cur.fetchall()
    return [
        {"id": r["id"], "name": r["name"], "contact": r["contact"], "num_participants": r["num_participants"],
         "participants": r["participants"], "teacher": r["teacher_in_charge"]}
        for r in rows
    ]


def update_sub_event(username, sub_event_id, name, contact, num_participants, participants, teacher_in_charge):
    init_events_tables()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE sub_events se
                   SET name=%s, contact=%s, num_participants=%s, participants=%s, teacher_in_charge=%s
                   FROM events e
                   WHERE se.event_id = e.id AND se.id=%s AND e.username=%s""",
                (name, contact, num_participants, participants, teacher_in_charge, sub_event_id, username)
            )
            conn.commit()


def delete_sub_event(username, sub_event_id):
    init_events_tables()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """DELETE FROM sub_events se
                   USING events e
                   WHERE se.event_id = e.id AND se.id=%s AND e.username=%s""",
                (sub_event_id, username)
            )
            conn.commit()
