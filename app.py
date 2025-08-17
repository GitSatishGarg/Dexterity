from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import database
import datetime

app = Flask(__name__)
app.secret_key = "supersecret"

# ----------------- INIT DB -----------------
database.init_db()


# ----------------- AUTH -----------------
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = database.get_user(username)
    if user and user['password'] == password:
        session['username'] = username
        return redirect(url_for('index'))

    return render_template("index.html", events=[], show_login=True, error="Invalid credentials")


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    try:
        database.add_user(username, password)
        return redirect(url_for('login'))
    except Exception:
        return render_template("index.html", events=[], show_login=True, error="Username already exists")


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


# ----------------- MAIN -----------------
@app.route('/')
def index():
    username = session.get("username")
    if not username:
        return render_template("index.html", events=[], username=None, show_login=True)

    events = database.get_all_events(username)
    for e in events:
        if isinstance(e['date'], (datetime.date, datetime.datetime)):
            e['date'] = e['date'].isoformat()
        e["sub_events"] = database.get_sub_events(e['id'])
    return render_template("index.html", events=events, username=username)


# ----------------- EVENTS -----------------
@app.route('/add', methods=['POST'])
def add():
    username = session.get("username")
    if not username:
        return redirect(url_for('index'))

    name = request.form.get('name')
    date = request.form.get('date')
    location = request.form.get('location')
    description = request.form.get('description')
    old_id = request.form.get('old_id')

    if old_id:
        database.update_event(int(old_id), name, date, location, description)
    elif name and date and location:
        database.add_event(username, name, date, location, description)
    return redirect(url_for('index'))


@app.route('/delete/<int:event_id>', methods=['POST'])
def delete(event_id):
    database.delete_event(event_id)
    return redirect(url_for('index'))


# ----------------- SUB-EVENTS -----------------
@app.route('/add_sub', methods=['POST'])
def add_sub():
    sub_id = request.form.get('sub_id')
    event_id = int(request.form.get('event_id'))
    name = request.form.get('name')
    contact = request.form.get('contact')
    num_participants = request.form.get('num_participants')
    participants = request.form.get('participants')
    teacher = request.form.get('teacher')

    if sub_id:
        database.update_sub_event(int(sub_id), name, contact, num_participants, participants, teacher)
    else:
        database.add_sub_event(event_id, name, contact, num_participants, participants, teacher)
    return redirect(url_for('index'))


@app.route('/delete_sub/<int:sub_id>', methods=['POST'])
def delete_sub(sub_id):
    database.delete_sub_event(sub_id)
    return redirect(url_for('index'))


@app.route('/get_sub_events/<int:event_id>')
def get_sub_events_route(event_id):
    sub_events = database.get_sub_events(event_id)
    return jsonify(sub_events)


# ----------------- RUN -----------------
if __name__ == "__main__":
    app.run(debug=True)
