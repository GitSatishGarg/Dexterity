from flask import Flask, render_template, request, redirect, url_for
import database as database

app = Flask(__name__)

@app.route('/')
def index():
    events = database.get_events()  # returns namedtuples
    # convert namedtuples to dicts
    events_data = [
        {
            "id": e.id,
            "name": e.name,
            "date": e.date,
            "location": e.location,
            "description": e.description
        }
        for e in events
    ]
    return render_template('index.html', events=events_data)



@app.route('/add', methods=['POST'])
def add():
    name = request.form.get('name')
    date = request.form.get('date')
    location = request.form.get('location')
    description = request.form.get('description')
    old_id = request.form.get('old_id')

    # If editing, delete old entry first
    if old_id:
        database.delete_event(int(old_id))

    if name and date and location:
        database.add_event(name, date, location, description)
    return redirect(url_for('index'))


@app.route('/edit/<int:event_id>', methods=['POST'])
def edit(event_id):
    name = request.form.get('name')
    date = request.form.get('date')
    location = request.form.get('location')
    description = request.form.get('description')
    if name and date and location:
        database.update_event(event_id, name, date, location, description)
    return redirect(url_for('index'))

@app.route('/delete/<int:event_id>', methods=['POST'])
def delete(event_id):
    database.delete_event(event_id)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
