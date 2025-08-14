from flask import Flask, render_template, request, redirect, url_for
import database as database

app = Flask(__name__)

# Database is already initialized on import, so no decorator needed

@app.route('/')
def index():
    events = database.get_events()
    return render_template('index.html', events=events)

@app.route('/add', methods=['POST'])
def add():
    name = request.form.get('name')
    date = request.form.get('date')
    location = request.form.get('location')
    description = request.form.get('description')  # optional field
    if name and date and location:
        database.add_event(name, date, location, description)
    return redirect(url_for('index'))

@app.route('/delete/<int:event_id>')
def delete(event_id):
    database.delete_event(event_id)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
