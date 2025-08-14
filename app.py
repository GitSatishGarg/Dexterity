from flask import Flask, render_template, request, redirect
import database

app = Flask(__name__)

# Initialize DB
database.init_db()

@app.route("/")
def index():
    events = database.get_events()
    return render_template("index.html", events=events)

@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name")
    date = request.form.get("date")
    location = request.form.get("location")
    database.add_event(name, date, location)
    return redirect("/")


@app.route("/delete/<int:event_id>")
def delete(event_id):
    database.delete_event(event_id)
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
