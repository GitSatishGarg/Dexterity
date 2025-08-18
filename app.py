from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import database

app = Flask(__name__)
app.secret_key = "supersecretkey"

database.init_db()

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]
    user_id = database.create_user(username, password)
    if not user_id:
        return "Username already exists", 400
    session["user_id"] = user_id
    session["username"] = username
    return redirect("/")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    user_id = database.authenticate_user(username, password)
    if user_id:
        session["user_id"] = user_id
        session["username"] = username
        return redirect("/")
    return "Invalid credentials", 401

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/", methods=["GET"])
def index():
    user_id = session.get("user_id")
    username = session.get("username")
    events = database.get_all_events(user_id) if user_id else database.get_all_events()
    return render_template("index.html", username=username, events=events)

@app.route("/add", methods=["POST"])
def add():
    user_id = session.get("user_id")
    if not user_id:
        return "Not logged in", 401

    name = request.form.get("name")
    date = request.form.get("date")
    location = request.form.get("location")
    description = request.form.get("description") or ""
    old_id = request.form.get("old_id")

    if old_id:
        database.edit_event(int(old_id), name, date, location, description)
    else:
        database.add_event(user_id, name, date, location, description)

    return redirect("/")

@app.route("/delete/<int:event_id>", methods=["POST"])
def delete(event_id):
    database.delete_event(event_id)
    return redirect("/")

@app.route("/get_sub_events/<int:event_id>", methods=["GET"])
def get_sub_events(event_id):
    subs = database.get_sub_events(event_id)
    return jsonify([dict(s) for s in subs])

@app.route("/add_sub", methods=["POST"])
def add_sub():
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
    if num_participants:
        try:
            num_participants = int(num_participants)
        except ValueError:
            num_participants = None
    else:
        num_participants = None

    sub_id = request.form.get("sub_id")
    if sub_id:
        database.edit_sub_event(
            int(sub_id), int(event_id), name, contact, num_participants, participants, teacher
        )
    else:
        database.add_sub_event(int(event_id), name, contact, num_participants, participants, teacher)

    return redirect("/")

@app.route("/delete_sub/<int:sub_id>", methods=["POST"])
def delete_sub(sub_id):
    database.delete_sub_event(sub_id)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
