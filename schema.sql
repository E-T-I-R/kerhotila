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