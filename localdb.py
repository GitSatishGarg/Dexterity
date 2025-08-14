import sqlite3

DB_NAME = "events.db"

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
            location TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def get_events():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM events ORDER BY id ASC")
    events = c.fetchall()
    conn.close()
    return events

def add_event(name, date, location):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO events (name, date, location) VALUES (?, ?, ?)",
        (name, date, location)
    )
    conn.commit()
    conn.close()

def delete_event(event_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()
