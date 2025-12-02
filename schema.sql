CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE reservations (
    id INTEGER PRIMARY KEY,
    title TEXT,
    time DATE,
    description TEXT,
    user_id INTEGER REFERENCES users
);

CREATE TABLE registrations (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    reservation_id INTEGER REFERENCES reservations
);