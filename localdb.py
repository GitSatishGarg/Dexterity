import sqlite3
from collections import namedtuple

DB_NAME = "events.db"
Event = namedtuple("Event", ["id", "name", "date", "location", "description"])

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_events():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, date, location, description FROM events ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    return [Event(*row) for row in rows]

def add_event(name, date, location, description=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO events (name, date, location, description) VALUES (?, ?, ?, ?)",
        (name, date, location, description)
    )
    conn.commit()
    conn.close()

def update_event(event_id, name, date, location, description=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE events
        SET name = ?, date = ?, location = ?, description = ?
        WHERE id = ?
    """, (name, date, location, description, event_id))
    conn.commit()
    conn.close()


def delete_event(event_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()

init_db()
