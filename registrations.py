import db

def add_registration(user_id, reservation_id):
    sql = "INSERT INTO registrations (user_id, reservation_id) VALUES (?,?)"
    db.execute(sql, [user_id, reservation_id])

def get_registrations():
    sql = """SELECT u.username
             FROM registrations reg, users u, reservations res
             WHERE reg.user_id = u.id AND reg.reservation_id = res.id
             ORDER BY reg.id"""
    return db.query(sql)