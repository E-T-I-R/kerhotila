import db

def add_reservation(title, time, description, user_id):
    sql = "INSERT INTO reservations (title, time, description, user_id) VALUES (?,?,?,?)"
    db.execute(sql, [title, time, description, user_id])
    reservation_id = db.last_insert_id()
    return reservation_id

def get_reservations():
    sql = "SELECT id, title, time FROM reservations ORDER BY id DESC"
    return db.query(sql)

def get_reservation(reservation_id):
    sql = """SELECT r.id, r.title, u.username, r.time, r.description, r.user_id
             FROM reservations r, users u
             WHERE r.user_id = u.id AND r.id = ?"""
    return db.query(sql, [reservation_id])[0]