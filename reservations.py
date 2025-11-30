import db

def get_reservations(title, time, description, user_id):
    sql = "INSERT INTO reservations (title, time, description, user_id) VALUES (?,?,?,?)"
    db.execute(sql, [title, time, description, user_id])