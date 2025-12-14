import db

def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        classes[title] = []
    for title, value in result:
        classes[title].append(value)

    return classes

def add_reservation(title, time, description, user_id, classes):
    sql = """INSERT INTO reservations (title, time, description, user_id)
             VALUES (?, ?, ?, ?)"""
    db.execute(sql, [title, time, description, user_id])

    reservation_id = db.last_insert_id()

    sql = """INSERT INTO reservation_classes (reservation_id, title, value)
             VALUES (?, ?, ?)"""
    for title, value in classes:
        db.execute(sql, [reservation_id, title, value])

    return reservation_id

def get_classes(reservation_id):
    sql = "SELECT title, value FROM reservation_classes WHERE reservation_id = ?"
    return db.query(sql, [reservation_id])

def get_reservations(page, page_size):
    sql = """SELECT r.id id,
                    r.title,
                    r.time,
                    r.user_id,
                    username
             FROM reservations r, users
             WHERE r.user_id = users.id
             ORDER BY r.time
             LIMIT ? OFFSET ?"""
    limit = page_size
    offset = page_size * (page - 1)
    return db.query(sql, [limit, offset])

def get_reservation(reservation_id):
    sql = """SELECT r.id, r.title, u.username, r.time, r.description, r.user_id
             FROM reservations r, users u
             WHERE r.user_id = u.id AND r.id = ?"""
    result = db.query(sql, [reservation_id])
    return result[0] if result else None

def update_reservation(reservation_id, title, time, description, classes):
    sql = "UPDATE reservations SET title = ?, time = ?, description = ? WHERE id = ?"
    db.execute(sql, [title, time, description, reservation_id])

    remove_classes(reservation_id)

    sql = """INSERT INTO reservation_classes (reservation_id, title, value)
             VALUES (?, ?, ?)"""
    for title, value in classes:
        db.execute(sql, [reservation_id, title, value])

def remove_reservation(reservation_id):
    sql = "DELETE FROM reservations WHERE id = ?"
    db.execute(sql, [reservation_id])

def remove_registrations(reservation_id):
    sql = "DELETE FROM registrations WHERE reservation_id = ?"
    db.execute(sql, [reservation_id])

def remove_classes(reservation_id):
    sql = "DELETE FROM reservation_classes WHERE reservation_id = ?"
    db.execute(sql, [reservation_id])

def search(query):
    sql = """SELECT r.id reservation_id,
                    r.title reservation_title,
                    r.time reservation_time,
                    u.username
             FROM reservations r, users u
             WHERE r.user_id = u.id AND
                   r.description LIKE ?
             ORDER BY r.title DESC"""
    return db.query(sql, ["%" + query + "%"])

def reservation_count():
    sql = "SELECT count(id) FROM reservations"
    return db.query(sql)[0][0]