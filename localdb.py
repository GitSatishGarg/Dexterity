import sqlite3

DB_NAME = "events.db"


def init_users_table():
    with sqlite3.connect(DB_NAME, timeout=10) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.commit()


def create_user_events_table(username):
    events_table = f"events_{username}"
    sub_events_table = f"sub_events_{username}"
    with sqlite3.connect(DB_NAME, timeout=10) as conn:
        c = conn.cursor()
        c.execute(f"""
            CREATE TABLE IF NOT EXISTS {events_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date TEXT NOT NULL,
                location TEXT NOT NULL,
                description TEXT
            )
        """)
        c.execute(f"""
            CREATE TABLE IF NOT EXISTS {sub_events_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                contact TEXT,
                num_participants INTEGER,
                participants TEXT,
                teacher_in_charge TEXT,
                FOREIGN KEY (event_id) REFERENCES {events_table}(id) ON DELETE CASCADE
            )
        """)
        conn.commit()


def add_user(username, password):
    init_users_table()
    with sqlite3.connect(DB_NAME, timeout=10) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
    create_user_events_table(username)


def get_user(username):
    init_users_table()
    with sqlite3.connect(DB_NAME, timeout=10) as conn:
        c = conn.cursor()
        c.execute("SELECT id, username, password FROM users WHERE username=?", (username,))
        return c.fetchone()


def add_event(username, name, date, location, description):
    create_user_events_table(username)
    table = f"events_{username}"
    with sqlite3.connect(DB_NAME, timeout=10) as conn:
        c = conn.cursor()
        c.execute(
            f"INSERT INTO {table} (name, date, location, description) VALUES (?, ?, ?, ?)",
            (name, date, location, description),
        )
        conn.commit()


def get_all_events(username):
    create_user_events_table(username)
    table = f"events_{username}"
    with sqlite3.connect(DB_NAME, timeout=10) as conn:
        c = conn.cursor()
        c.execute(f"SELECT id, name, date, location, description FROM {table}")
        rows = c.fetchall()
    return [
        {"id": r[0], "name": r[1], "date": r[2], "location": r[3], "description": r[4]}
        for r in rows
    ]


def delete_event(username, event_id):
    create_user_events_table(username)
    table = f"events_{username}"
    with sqlite3.connect(DB_NAME, timeout=10) as conn:
        c = conn.cursor()
        c.execute(f"DELETE FROM {table} WHERE id = ?", (event_id,))
        conn.commit()


def update_event(username, event_id, name, date, location, description):
    create_user_events_table(username)
    table = f"events_{username}"
    with sqlite3.connect(DB_NAME, timeout=10) as conn:
        c = conn.cursor()
        c.execute(
            f"UPDATE {table} SET name=?, date=?, location=?, description=? WHERE id=?",
            (name, date, location, description, event_id),
        )
        conn.commit()


def add_sub_event(username, event_id, name, contact, num_participants, participants, teacher_in_charge):
    create_user_events_table(username)
    table = f"sub_events_{username}"
    with sqlite3.connect(DB_NAME, timeout=10) as conn:
        c = conn.cursor()
        c.execute(
            f"""INSERT INTO {table}
                (event_id, name, contact, num_participants, participants, teacher_in_charge)
                VALUES (?, ?, ?, ?, ?, ?)""",
            (event_id, name, contact, num_participants, participants, teacher_in_charge),
        )
        conn.commit()


def get_sub_events(username, event_id):
    create_user_events_table(username)
    table = f"sub_events_{username}"
    with sqlite3.connect(DB_NAME, timeout=10) as conn:
        c = conn.cursor()
        c.execute(
            f"""SELECT id, name, contact, num_participants, participants, teacher_in_charge
                FROM {table} WHERE event_id=?""",
            (event_id,),
        )
        rows = c.fetchall()
    return [
        {"id": r[0], "name": r[1], "contact": r[2], "num_participants": r[3],
         "participants": r[4], "teacher": r[5]}
        for r in rows
    ]


def delete_sub_event(username, sub_event_id):
    create_user_events_table(username)
    table = f"sub_events_{username}"
    with sqlite3.connect(DB_NAME, timeout=10) as conn:
        c = conn.cursor()
        c.execute(f"DELETE FROM {table} WHERE id=?", (sub_event_id,))
        conn.commit()


def update_sub_event(username, sub_event_id, name, contact, num_participants, participants, teacher_in_charge):
    create_user_events_table(username)
    table = f"sub_events_{username}"
    with sqlite3.connect(DB_NAME, timeout=10) as conn:
        c = conn.cursor()
        c.execute(
            f"""UPDATE {table}
                SET name=?, contact=?, num_participants=?, participants=?, teacher_in_charge=?
                WHERE id=?""",
            (name, contact, num_participants, participants, teacher_in_charge, sub_event_id),
        )
        conn.commit()
