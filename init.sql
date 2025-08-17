-- init.sql

-- ----------------- USERS -----------------
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- ----------------- EVENTS -----------------
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    date DATE NOT NULL,
    location TEXT NOT NULL,
    description TEXT
);

-- ----------------- SUB-EVENTS -----------------
CREATE TABLE IF NOT EXISTS sub_events (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    contact TEXT,
    num_participants INTEGER,
    participants TEXT,
    teacher_in_charge TEXT
);
