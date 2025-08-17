from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import database

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Initialize DB tables
database.init_db()

# ---------------- AUTH ----------------
@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    if username and password:
        database.add_user(username, password)
    return redirect("/")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    user = database.get_user(username)
    if user and user["password"] == password:
        session["user_id"] = user["id"]
        session["username"] = user["username"]
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- EVENTS ----------------
@app.route("/")
def index():
    if "user_id" not in session:
        return render_template("index.html", events=[], username=None)

    user_id = session["user_id"]
    username = session["username"]
    events = database.get_all_events(user_id)
    return render_template("index.html", events=events, username=username)

@app.route("/add", methods=["POST"])
def add():
    if "user_id" not in session:
        return redirect("/")

    user_id = session["user_id"]
    name = request.form.get("name")
    date = request.form.get("date")
    location = request.form.get("location")
    description = request.form.get("description") or None

    old_id = request.form.get("old_id")
    if old_id:  # Editing existing event
        database.update_event(old_id, name, date, location, description)
    else:       # Adding new event
        database.add_event(user_id, name, date, location, description)

    return redirect("/")

@app.route("/delete/<int:event_id>", methods=["POST"])
def delete(event_id):
    database.delete_event(event_id)
    return redirect("/")


# ---------------- SUB-EVENTS ----------------
@app.route("/add_sub", methods=["POST"])
def add_sub():
    if "user_id" not in session:
        return redirect("/")

    event_id = request.form.get("event_id")
    name = request.form.get("name")
    contact = request.form.get("contact") or None
    num_participants = request.form.get("num_participants") or None
    participants = request.form.get("participants") or None
    teacher = request.form.get("teacher") or None

    sub_id = request.form.get("sub_id")
    if sub_id:  # Editing existing sub-event
        database.update_sub_event(sub_id, name, contact, num_participants, participants, teacher)
    else:       # Adding new sub-event
        database.add_sub_event(event_id, name, contact, num_participants, participants, teacher)

    return redirect("/")

@app.route("/delete_sub/<int:sub_id>", methods=["POST"])
def delete_sub(sub_id):
    database.delete_sub_event(sub_id)
    return redirect("/")

@app.route("/get_sub_events/<int:event_id>")
def get_sub_events(event_id):
    subs = database.get_sub_events(event_id)
    return jsonify(subs)


if __name__ == "__main__":
    app.run(debug=True)
