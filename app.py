import sqlite3
from flask import Flask, redirect, render_template, request, session, abort, make_response, flash
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

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", filled={})

    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if not username or not password1 or not password2 or len(username) > 20 or len(password1) > 100 or len(password2) > 100:
            abort(403)

        if password1 != password2:
            flash("VIRHE: Antamasi salasanat eivät ole samat")
            filled = {"username": username}
            return render_template("register.html", filled=filled)

        if users.create_user(username, password1):
            flash("Tunnuksen luominen onnistui, voit nyt kirjautua sisään")
            return redirect("/")
        else:
            flash("VIRHE: Valitsemasi tunnus on jo varattu")
            filled = {"username": username}
            return render_template("register.html", filled=filled)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", next_page=request.referrer)

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        next_page = request.form["next_page"]
        if not username or not password or len(username) > 20 or len(password) > 100:
            abort(403)

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["csrf_token"] = secrets.token_hex(16)
            session["username"] = username
            return redirect(next_page)
        else:
            flash("VIRHE: Väärä tunnus tai salasana")
            return render_template("login.html", next_page=next_page)

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
    classes = reservations.get_all_classes()

    return render_template("new_reservation.html", classes=classes)

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

    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            parts = entry.split(":")
            classes.append((parts[0], parts[1]))

    reservation_id = reservations.add_reservation(title, time, description, user_id, classes)

    return redirect("/reservation/" + str(reservation_id))

@app.route("/reservation/<int:reservation_id>")
def show_reservation(reservation_id):
    reservation = reservations.get_reservation(reservation_id)
    if not reservation:
        abort(404)
    classes = reservations.get_classes(reservation_id)
    event_registrations = registrations.get_registrations()

    return render_template("show_reservation.html", reservation=reservation, registrations=event_registrations, classes=classes)

@app.route("/edit/<int:reservation_id>", methods=["GET", "POST"])
def edit_reservation(reservation_id):
    require_login()

    reservation = reservations.get_reservation(reservation_id)
    if not reservation:
        abort(404)
    if reservation["user_id"] != session["user_id"]:
        abort(403)

    all_classes = reservations.get_all_classes()
    classes = {}
    for my_class in all_classes:
        classes[my_class] = ""
    for entry in reservations.get_classes(reservation_id):
        classes[entry["title"]] = entry["value"]

    if request.method == "GET":
        return render_template("edit.html", reservation=reservation, classes=classes, all_classes=all_classes)

    if request.method == "POST":
        check_csrf()

        title = request.form["title"]
        time = request.form["time"]
        description = request.form["description"]
        if not title or len(title) > 50 or len(description) > 5000:
            abort(403)

        classes = []
        for entry in request.form.getlist("classes"):
            if entry:
                parts = entry.split(":")
                classes.append((parts[0], parts[1]))

        reservations.update_reservation(reservation_id, title, time, description, classes)

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
            reservations.remove_classes(reservation_id)
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
            flash("VIRHE: Lähettämäsi tiedosto ei ole jpg-tiedosto")
            return redirect("/add_image")

        image = file.read()
        if len(image) > 100 * 1024:
            flash("VIRHE: Lähettämäsi kuva on liian suuri")
            return redirect("/add_image")

        user_id = session["user_id"]
        users.update_image(user_id, image)
        flash("Kuvan lisääminen onnistui")
        return redirect("/user/" + str(user_id))

@app.route("/image/<int:user_id>")
def show_image(user_id):
    image = users.get_image(user_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/jpeg")
    return response