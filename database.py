import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")


def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


# ---------------- USERS ----------------
def init_users_table():
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            conn.commit()


def add_user(username, password):
    init_users_table()
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, password)
            )
            conn.commit()
    create_user_events_table(username)


def get_user(username):
    init_users_table()
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute("SELECT id, username, password FROM users WHERE username=%s", (username,))
            return c.fetchone()


# ---------------- CREATE USER TABLES ----------------
def create_user_events_table(username):
    events_table = f"events_{username}"
    sub_events_table = f"sub_events_{username}"

    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute(f"""
                CREATE TABLE IF NOT EXISTS {events_table} (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    date DATE NOT NULL,
                    location TEXT NOT NULL,
                    description TEXT
                )
            """)
            c.execute(f"""
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
            conn.commit()


# ---------------- EVENTS ----------------
def add_event(username, name, date, location, description):
    create_user_events_table(username)
    table = f"events_{username}"
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute(
                f"INSERT INTO {table} (name, date, location, description) VALUES (%s, %s, %s, %s)",
                (name, date, location, description)
            )
            conn.commit()


def get_all_events(username):
    create_user_events_table(username)
    table = f"events_{username}"
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute(f"SELECT id, name, date, location, description FROM {table} ORDER BY date")
            rows = c.fetchall()
    return [
        {"id": r["id"], "name": r["name"], "date": str(r["date"]), "location": r["location"], "description": r["description"]}
        for r in rows
    ]


def update_event(username, event_id, name, date, location, description):
    create_user_events_table(username)
    table = f"events_{username}"
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute(
                f"UPDATE {table} SET name=%s, date=%s, location=%s, description=%s WHERE id=%s",
                (name, date, location, description, event_id)
            )
            conn.commit()


def delete_event(username, event_id):
    create_user_events_table(username)
    table = f"events_{username}"
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute(f"DELETE FROM {table} WHERE id=%s", (event_id,))
            conn.commit()


# ---------------- SUB-EVENTS ----------------
def add_sub_event(username, event_id, name, contact, num_participants, participants, teacher_in_charge):
    create_user_events_table(username)
    table = f"sub_events_{username}"
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute(
                f"""INSERT INTO {table}
                   (event_id, name, contact, num_participants, participants, teacher_in_charge)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (event_id, name, contact, num_participants, participants, teacher_in_charge)
            )
            conn.commit()


def get_sub_events(username, event_id):
    create_user_events_table(username)
    table = f"sub_events_{username}"
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute(
                f"""SELECT id, name, contact, num_participants, participants, teacher_in_charge
                   FROM {table} WHERE event_id=%s""",
                (event_id,)
            )
            rows = c.fetchall()
    return [
        {"id": r["id"], "name": r["name"], "contact": r["contact"],
         "num_participants": r["num_participants"], "participants": r["participants"],
         "teacher": r["teacher_in_charge"]}
        for r in rows
    ]


def update_sub_event(username, sub_event_id, name, contact, num_participants, participants, teacher_in_charge):
    create_user_events_table(username)
    table = f"sub_events_{username}"
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute(
                f"""UPDATE {table}
                   SET name=%s, contact=%s, num_participants=%s, participants=%s, teacher_in_charge=%s
                   WHERE id=%s""",
                (name, contact, num_participants, participants, teacher_in_charge, sub_event_id)
            )
            conn.commit()


def delete_sub_event(username, sub_event_id):
    create_user_events_table(username)
    table = f"sub_events_{username}"
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute(f"DELETE FROM {table} WHERE id=%s", (sub_event_id,))
            conn.commit()
