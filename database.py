import sqlite3

DB_NAME = "events.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            location TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def get_events():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM events")
    events = c.fetchall()
    conn.close()
    return events

def add_event(name, date, location):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO events (name, date, location) VALUES (?, ?, ?)",
              (name, date, location))
    conn.commit()
    conn.close()

def delete_event(event_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()
