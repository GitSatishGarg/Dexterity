-- ---------------- USERS TABLE ----------------
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- ---------------- EVENTS TABLE ----------------
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    date DATE NOT NULL,
    location TEXT NOT NULL,
    description TEXT
);

-- ---------------- SUB-EVENTS TABLE ----------------
CREATE TABLE IF NOT EXISTS sub_events (
    id SERIAL PRIMARY KEY,
    event_id INT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    contact TEXT,
    num_participants INT,
    participants TEXT,
    teacher_in_charge TEXT
);

-- Optional: Sample user
INSERT INTO users (username, password) VALUES ('admin', 'admin123') ON CONFLICT DO NOTHING;

-- Optional: Sample event
INSERT INTO events (user_id, name, date, location, description)
VALUES (1, 'Sample Event', '2025-08-17', 'Auditorium', 'This is a sample event')
ON CONFLICT DO NOTHING;

-- Optional: Sample sub-event
INSERT INTO sub_events (event_id, name, contact, num_participants, participants, teacher_in_charge)
VALUES (1, 'Sample Sub-Event', 'John Doe', 5, 'Alice,Bob,Charlie', 'Mr. Smith')
ON CONFLICT DO NOTHING;
