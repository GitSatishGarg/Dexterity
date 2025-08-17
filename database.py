import os
import psycopg2  # type: ignore
from psycopg2.extras import RealDictCursor  # type: ignore

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


def add_user(username, password):
    init_users_table()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, password)
            )
    # Automatically create per-user tables
    create_user_tables(username)


def get_user(username):
    init_users_table()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, username, password FROM users WHERE username=%s", (username,))
            return cur.fetchone()


# ---------------- PER-USER TABLES ----------------
def create_user_tables(username):
    events_table = f"events_{username}"
    sub_events_table = f"sub_events_{username}"

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Events table
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {events_table} (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    date DATE NOT NULL,
                    location TEXT NOT NULL,
                    description TEXT
                )
            """)
            # Sub-events table
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {sub_events_table} (
                    id SERIAL PRIMARY KEY,
                    event_id INTEGER NOT NULL REFERENCES {events_table}(id) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    contact TEXT,
                    num_participants INTEGER,
                    participants TEXT,
                    teacher_in_charge TEXT
                )
            """)


# ---------------- EVENTS ----------------
def add_event(username, name, date, location, description):
    create_user_tables(username)
    table = f"events_{username}"
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {table} (name, date, location, description) VALUES (%s, %s, %s, %s)",
                (name, date, location, description)
            )


def get_all_events(username):
    create_user_tables(username)
    table = f"events_{username}"
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT id, name, date, location, description FROM {table} ORDER BY date")
            return cur.fetchall()


def update_event(username, event_id, name, date, location, description):
    create_user_tables(username)
    table = f"events_{username}"
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE {table} SET name=%s, date=%s, location=%s, description=%s WHERE id=%s",
                (name, date, location, description, event_id)
            )


def delete_event(username, event_id):
    create_user_tables(username)
    table = f"events_{username}"
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM {table} WHERE id=%s", (event_id,))


# ---------------- SUB-EVENTS ----------------
def add_sub_event(username, event_id, name, contact, num_participants, participants, teacher_in_charge):
    create_user_tables(username)
    table = f"sub_events_{username}"
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""INSERT INTO {table} 
                    (event_id, name, contact, num_participants, participants, teacher_in_charge)
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                (event_id, name, contact, num_participants, participants, teacher_in_charge)
            )


def get_sub_events(username, event_id):
    create_user_tables(username)
    table = f"sub_events_{username}"
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""SELECT id, name, contact, num_participants, participants, teacher_in_charge
                    FROM {table} WHERE event_id=%s""",
                (event_id,)
            )
            return cur.fetchall()


def update_sub_event(username, sub_event_id, name, contact, num_participants, participants, teacher_in_charge):
    create_user_tables(username)
    table = f"sub_events_{username}"
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""UPDATE {table}
                    SET name=%s, contact=%s, num_participants=%s, participants=%s, teacher_in_charge=%s
                    WHERE id=%s""",
                (name, contact, num_participants, participants, teacher_in_charge, sub_event_id)
            )


def delete_sub_event(username, sub_event_id):
    create_user_tables(username)
    table = f"sub_events_{username}"
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM {table} WHERE id=%s", (sub_event_id,))
