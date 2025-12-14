CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    image BLOB
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

CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    title TEXT,
    value TEXT
);

CREATE TABLE reservation_classes (
    id INTEGER PRIMARY KEY,
    reservation_id INTEGER REFERENCES reservations,
    title TEXT,
    value TEXT
);