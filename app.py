from flask import Flask, render_template, request, redirect, session, jsonify, send_file
import localdb as database
import csv

app = Flask(__name__)
app.secret_key = "key"

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]
    if database.get_user(username):
        return "Username already exists", 400
    database.add_user(username, password)
    session["username"] = username
    return redirect("/")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    user = database.get_user(username)
    if user and user[2] == password:
        session["username"] = username
        return redirect("/")
    return "Invalid credentials", 401

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/", methods=["GET"])
def index():
    username = session.get("username")
    events = database.get_all_events(username) if username else []
    return render_template("index.html", username=username, events=events)

@app.route("/add", methods=["POST"])
def add():
    username = session.get("username")
    if not username:
        return "Not logged in", 401
    name = request.form.get("name")
    date = request.form.get("date")
    location = request.form.get("location")
    description = request.form.get("description") or ""
    old_id = request.form.get("old_id")
    if old_id:
        database.update_event(username, int(old_id), name, date, location, description)
    else:
        database.add_event(username, name, date, location, description)
    return redirect("/")

@app.route("/delete/<int:event_id>", methods=["POST"])
def delete(event_id):
    username = session.get("username")
    if not username:
        return "Not logged in", 401
    database.delete_event(username, event_id)
    return redirect("/")

@app.route("/get_sub_events/<int:event_id>", methods=["GET"])
def get_sub_events(event_id):
    username = session.get("username")
    if not username:
        return jsonify([])
    subs = database.get_sub_events(username, event_id)
    return jsonify(subs)

@app.route("/add_sub", methods=["POST"])
def add_sub():
    username = session.get("username")
    if not username:
        return "Not logged in", 401
    event_id = request.form.get("event_id")
    if not event_id:
        return "Missing event ID", 400
    name = request.form.get("name")
    if not name:
        return "Sub-event name required", 400
    contact = request.form.get("contact") or None
    participants = request.form.get("participants") or None
    teacher = request.form.get("teacher") or None
    num_participants = request.form.get("num_participants")
    try:
        num_participants = int(num_participants) if num_participants else None
    except ValueError:
        num_participants = None
    sub_id = request.form.get("sub_id")
    if sub_id:
        database.update_sub_event(username, int(sub_id), name, contact, num_participants, participants, teacher)
    else:
        database.add_sub_event(username, int(event_id), name, contact, num_participants, participants, teacher)
    return redirect("/")

@app.route("/delete_sub/<int:sub_id>", methods=["POST"])
def delete_sub(sub_id):
    username = session.get("username")
    if not username:
        return "Not logged in", 401
    database.delete_sub_event(username, sub_id)
    return redirect("/")

@app.route("/export_events_csv")
def export_events_csv():
    username = session.get("username")
    if not username:
        return redirect("/")
    table = f"events_{username}"
    with open("events.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Date", "Location", "Description"])
        with database.sqlite3.connect(database.DB_NAME, timeout=10) as conn:
            c = conn.cursor()
            c.execute(f"SELECT id, name, date, location, description FROM {table}")
            writer.writerows(c.fetchall())
    return send_file("events.csv", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
