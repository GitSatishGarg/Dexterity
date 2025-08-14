import os
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
# Use DATABASE_URL if present (Render Postgres), else SQLite
db_url = os.getenv("DATABASE_URL", "sqlite:///db.sqlite3")
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Example model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

@app.route("/")
def home():
    return "Event Portal is running!"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # quick bootstrapping
    app.run(host="0.0.0.0", port=5000)
