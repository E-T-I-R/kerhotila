import db

def add_registration(user_id, reservation_id):
    sql = "INSERT INTO registrations (user_id, reservation_id) VALUES (?,?)"
    db.execute(sql, [user_id, reservation_id])

def get_registrations():
    sql = """SELECT u.username, reg.id, reg.reservation_id
             FROM registrations reg, users u, reservations res
             WHERE reg.user_id = u.id AND reg.reservation_id = res.id
             ORDER BY reg.id"""
    return db.query(sql)

def get_reservation_id(registration_id):
    sql = """SELECT res.id
             FROM registrations reg, reservations res
             WHERE reg.reservation_id = res.id AND reg.id = ?
             ORDER BY reg.id"""
    return db.query(sql, [registration_id])[0][0]

def remove_registration(registration_id):
    sql = "DELETE FROM registrations WHERE id = ?"
    db.execute(sql, [registration_id])