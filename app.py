import sqlite3
from flask import Flask, redirect, render_template, request, session, abort, make_response, g
from werkzeug.security import check_password_hash, generate_password_hash
import math
import secrets
import config
import db
import reservations
import registrations
import users

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
@app.route("/<int:page>")
def index(page=1):
    page_size = 10
    reservation_count = reservations.reservation_count()
    page_count = math.ceil(reservation_count / page_size)
    page_count = max(page_count, 1)

    if page < 1:
        return redirect("/1")
    if page > page_count:
        return redirect("/" + str(page_count))

    all_reservations = reservations.get_reservations(page, page_size)
    return render_template("index.html", page=page, page_count=page_count, reservations=all_reservations)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if not username or not password1 or not password2 or len(username) > 20 or len(password1) > 100 or len(password2) > 100:
        abort(403)

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
        if not username or not password or len(username) > 20 or len(password) > 100:
            abort(403)

        sql = "SELECT id, password_hash FROM users WHERE username = ?"
        result = db.query(sql, [username])[0]
        user_id = result["id"]
        password_hash = result["password_hash"]

        if check_password_hash(password_hash, password):
            session["user_id"] = user_id
            session["csrf_token"] = secrets.token_hex(16)
            session["username"] = username
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    require_login()

    del session["username"]
    del session["user_id"]
    return redirect("/")

def require_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.route("/new_reservation")
def new_reservation():
    require_login()

    return render_template("new_reservation.html")

@app.route("/create_reservation", methods=["POST"])
def create_reservation():
    require_login()
    check_csrf()

    title = request.form["title"]
    time = request.form["time"]
    description = request.form["description"]
    user_id = session["user_id"]
    if not title or len(title) > 50 or len(description) > 5000:
        abort(403)

    reservation_id = reservations.add_reservation(title, time, description, user_id)

    return redirect("/reservation/" + str(reservation_id))

@app.route("/reservation/<int:reservation_id>")
def show_reservation(reservation_id):
    reservation = reservations.get_reservation(reservation_id)
    if not reservation:
        abort(404)
    event_registrations = registrations.get_registrations()

    return render_template("show_reservation.html", reservation=reservation, registrations=event_registrations)

@app.route("/edit/<int:reservation_id>", methods=["GET", "POST"])
def edit_reservation(reservation_id):
    require_login()

    reservation = reservations.get_reservation(reservation_id)
    if not reservation:
        abort(404)
    if reservation["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("edit.html", reservation=reservation)

    if request.method == "POST":
        check_csrf()

        title = request.form["title"]
        time = request.form["time"]
        description = request.form["description"]
        if not title or len(title) > 50 or len(description) > 5000:
            abort(403)

        reservations.update_reservation(reservation_id, title, time, description)

        return redirect("/reservation/" + str(reservation_id))

@app.route("/remove_reservation/<int:reservation_id>", methods=["GET", "POST"])
def remove_reservation(reservation_id):
    require_login()

    reservation = reservations.get_reservation(reservation_id)
    if not reservation:
        abort(404)
    elif reservation["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_reservation.html", reservation=reservation)

    if request.method == "POST":
        check_csrf()

        if "continue" in request.form:
            reservations.remove_registrations(reservation_id)
            reservations.remove_reservation(reservation_id)
            return redirect("/")

        return redirect("/reservation/" + str(reservation_id))

@app.route("/register_event", methods=["POST"])
def register_event():
    check_csrf()
    require_login()

    user_id = session["user_id"]
    reservation_id = request.form["reservation_id"]
    try:
        registrations.add_registration(user_id, reservation_id)
    except sqlite3.IntegrityError:
        abort(403)

    return redirect("/reservation/" + str(reservation_id))

@app.route("/remove_registration/<int:registration_id>")
def remove_registration(registration_id):
    require_login()

    registration = registrations.get_reservation_id(registration_id)
    if not registration:
        abort(404)
    if registration["user_id"] != session["user_id"]:
        abort(403)
    registrations.remove_registration(registration_id)

    return redirect("/reservation/" + str(registration["id"]))

@app.route("/search")
def search():
    query = request.args.get("query")
    results = reservations.search(query) if query else []
    return render_template("search.html", query=query, results=results)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    require_login()

    user = users.get_user(user_id)
    if not user:
        abort(404)
    reservations = users.get_reservations(user_id)
    registrations = users.get_registrations(user_id)
    return render_template("user.html", user=user, reservations=reservations, registrations=registrations)

@app.route("/add_image", methods=["GET", "POST"])
def add_image():
    require_login()

    if request.method == "GET":
        return render_template("add_image.html")

    if request.method == "POST":
        check_csrf()

        file = request.files["image"]
        if not file.filename.endswith(".jpg"):
            return "VIRHE: väärä tidostomuoto"

        image = file.read()
        if len(image) > 100 * 1024:
            return "VIRHE: liian suuri kuva"

        user_id = session["user_id"]
        users.update_image(user_id, image)
        return redirect("/user/" + str(user_id))

@app.route("/image/<int:user_id>")
def show_image(user_id):
    image = users.get_image(user_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/jpeg")
    return response