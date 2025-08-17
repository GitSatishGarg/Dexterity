from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)
app.secret_key = "supersecret"

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# ---------------- USERS ----------------
def add_user(username, password):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))

def get_user(username):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE username=%s", (username,))
            return cur.fetchone()

# ---------------- EVENTS ----------------
def add_event(user_id, name, date, location, description):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO events (user_id, name, date, location, description) VALUES (%s, %s, %s, %s, %s)",
                (user_id, name, date, location, description)
            )

def get_all_events(user_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM events WHERE user_id=%s ORDER BY date",
                (user_id,)
            )
            return cur.fetchall()

def update_event(event_id, name, date, location, description):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE events SET name=%s, date=%s, location=%s, description=%s WHERE id=%s",
                (name, date, location, description, event_id)
            )

def delete_event(event_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM events WHERE id=%s", (event_id,))

# ---------------- SUB-EVENTS ----------------
def add_sub_event(event_id, name, contact, num_participants, participants, teacher_in_charge):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO sub_events
                (event_id, name, contact, num_participants, participants, teacher_in_charge)
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (event_id, name, contact or None,
                 int(num_participants) if num_participants else None,
                 participants or None, teacher_in_charge or None)
            )

def get_sub_events(event_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM sub_events WHERE event_id=%s ORDER BY id",
                (event_id,)
            )
            return cur.fetchall()

def update_sub_event(sub_id, name, contact, num_participants, participants, teacher_in_charge):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE sub_events
                   SET name=%s, contact=%s, num_participants=%s, participants=%s, teacher_in_charge=%s
                   WHERE id=%s""",
                (name, contact or None,
                 int(num_participants) if num_participants else None,
                 participants or None, teacher_in_charge or None, sub_id)
            )

def delete_sub_event(sub_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM sub_events WHERE id=%s", (sub_id,))

# ---------------- FLASK ROUTES ----------------

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = get_user(username)
    if user and user['password'] == password:
        session['user_id'] = user['id']
        session['username'] = user['username']
        return redirect(url_for('index'))
    return render_template("index.html", events=[], show_login=True, error="Invalid credentials")

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    try:
        add_user(username, password)
        return redirect(url_for('login'))
    except:
        return render_template("index.html", events=[], show_login=True, error="Username already exists")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/')
def index():
    user_id = session.get("user_id")
    if not user_id:
        return render_template("index.html", events=[], username=None, show_login=True)

    events = get_all_events(user_id)
    for e in events:
        e["sub_events"] = get_sub_events(e["id"])
    return render_template("index.html", events=events, username=session.get("username"))

@app.route('/add', methods=['POST'])
def add():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for('index'))

    name = request.form.get('name')
    date = request.form.get('date')
    location = request.form.get('location')
    description = request.form.get('description')
    old_id = request.form.get('old_id')

    if old_id:
        update_event(int(old_id), name, date, location, description)
    elif name and date and location:
        add_event(user_id, name, date, location, description)

    return redirect(url_for('index'))

@app.route('/delete/<int:event_id>', methods=['POST'])
def delete(event_id):
    delete_event(event_id)
    return redirect(url_for('index'))

@app.route('/add_sub', methods=['POST'])
def add_sub():
    event_id = request.form.get('event_id')
    sub_id = request.form.get('sub_id')
    name = request.form.get('name')
    contact = request.form.get('contact')
    num_participants = request.form.get('num_participants')
    participants = request.form.get('participants')
    teacher = request.form.get('teacher')

    if sub_id:
        update_sub_event(int(sub_id), name, contact, num_participants, participants, teacher)
    else:
        add_sub_event(int(event_id), name, contact, num_participants, participants, teacher)

    return redirect(url_for('index'))

@app.route('/delete_sub/<int:sub_id>', methods=['POST'])
def delete_sub(sub_id):
    delete_sub_event(sub_id)
    return redirect(url_for('index'))

@app.route('/get_sub_events/<int:event_id>')
def get_sub_events_route(event_id):
    sub_events = get_sub_events(event_id)
    return jsonify([
        {"id": s['id'], "name": s['name'], "contact": s['contact'],
         "num_participants": s['num_participants'], "participants": s['participants'],
         "teacher": s['teacher_in_charge']}
        for s in sub_events
    ])

if __name__ == "__main__":
    app.run(debug=True)
