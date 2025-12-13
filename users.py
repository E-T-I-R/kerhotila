import db

def get_user(user_id):
    sql = """SELECT id, username, image IS NOT NULL has_image
             FROM users
             WHERE id = ?"""
    result = db.query(sql, [user_id])
    return result[0] if result else None

def get_reservations(user_id):
    sql = """SELECT r.id,
                    r.title,
                    r.time
             FROM reservations r
             WHERE r.user_id = ?
             ORDER BY r.time DESC"""
    return db.query(sql, [user_id])

def get_registrations(user_id):
    sql = """SELECT res.id reservation_id,
                    res.title reservation_title,
                    res.time reservation_time,
                    res.user_id reservation_user_id,
                    u.username reservation_username
             FROM registrations reg, reservations res, users u
             WHERE reg.reservation_id = res.id AND
                   res.user_id = u.id AND
                   reg.user_id = ?
             ORDER BY res.time DESC"""
    return db.query(sql, [user_id])

def update_image(user_id, image):
    sql = "UPDATE users SET image = ? WHERE id = ?"
    db.execute(sql, [image, user_id])

def get_image(user_id):
    sql = "SELECT image FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0][0] if result else None