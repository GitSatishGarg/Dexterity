import sqlite3

DB_NAME = "events.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        """)
        conn.commit()

def add_user(username, password):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        c.execute(f"""
            CREATE TABLE IF NOT EXISTS {username}_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                date TEXT,
                location TEXT,
                description TEXT
            )
        """)
        c.execute(f"""
            CREATE TABLE IF NOT EXISTS {username}_sub_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                name TEXT,
                contact TEXT,
                num_participants INTEGER,
                participants TEXT,
                teacher TEXT,
                FOREIGN KEY (event_id) REFERENCES {username}_events (id)
            )
        """)
        conn.commit()

def get_all_events(username):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute(f"""
            CREATE TABLE IF NOT EXISTS {username}_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                date TEXT,
                location TEXT,
                description TEXT
            )
        """)
        c.execute(f"SELECT * FROM {username}_events")
        return c.fetchall()

def get_sub_events(username, event_id):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute(f"""
            CREATE TABLE IF NOT EXISTS {username}_sub_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                name TEXT,
                contact TEXT,
                num_participants INTEGER,
                participants TEXT,
                teacher TEXT,
                FOREIGN KEY (event_id) REFERENCES {username}_events (id)
            )
        """)
        c.execute(f"SELECT * FROM {username}_sub_events WHERE event_id = ?", (event_id,))
        return c.fetchall()
