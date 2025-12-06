import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, abort
from werkzeug.security import check_password_hash, generate_password_hash
import config
import db
import reservations
import registrations

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    all_reservations = reservations.get_reservations()
    return render_template("index.html", reservations=all_reservations)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "<p>VIRHE: tunnus on jo varattu</p> <p><a href=""/"">Takaisin</a></p>"

    return "<p>Tunnus luotu</p> <p><a href=""/"">Takaisin</a></p>"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT id, password_hash FROM users WHERE username = ?"
        result = db.query(sql, [username])[0]
        user_id = result["id"]
        password_hash = result["password_hash"]

        if check_password_hash(password_hash, password):
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    del session["username"]
    del session["user_id"]
    return redirect("/")

@app.route("/new_reservation")
def new_reservation():
    return render_template("new_reservation.html")

@app.route("/create_reservation", methods=["POST"])
def create_reservation():
    title = request.form["title"]
    time = request.form["time"]
    description = request.form["description"]
    user_id = session["user_id"]

    reservation_id = reservations.add_reservation(title, time, description, user_id)

    return redirect("/reservation/" + str(reservation_id))

@app.route("/reservation/<int:reservation_id>")
def show_reservation(reservation_id):
    reservation = reservations.get_reservation(reservation_id)
    event_registrations = registrations.get_registrations()

    return render_template("show_reservation.html", reservation=reservation, registrations=event_registrations)

@app.route("/edit/<int:reservation_id>", methods=["GET", "POST"])
def edit_reservation(reservation_id):
    reservation = reservations.get_reservation(reservation_id)
    if reservation["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("edit.html", reservation=reservation)

    if request.method == "POST":
        title = request.form["title"]
        time = request.form["time"]
        description = request.form["description"]
        reservations.update_reservation(reservation_id, title, time, description)

        return redirect("/reservation/" + str(reservation_id))

@app.route("/remove/<int:reservation_id>", methods=["GET", "POST"])
def remove_reservation(reservation_id):
    reservation = reservations.get_reservation(reservation_id)
    if reservation["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove.html", reservation=reservation)

    if request.method == "POST":
        if "continue" in request.form:
            reservations.remove_registrations(reservation_id)
            reservations.remove_reservation(reservation_id)
            return redirect("/")

        return redirect("/reservation/" + str(reservation_id))

@app.route("/register_event", methods=["POST"])
def register_event():
    user_id = request.form["user_id"]
    reservation_id = request.form["reservation_id"]
    registrations.add_registration(user_id, reservation_id)

    return redirect("/reservation/" + str(reservation_id))

@app.route("/remove/<int:registration_id>")
def remove_registration(registration_id):
    registration = registrations.get_reservation_id(registration_id)
    registrations.remove_registration(registration_id)

    return redirect("/reservation/" + str(registration))