import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, is_valid, get_userd

from datetime import datetime

# Get today's date
time = datetime.now()

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///somos2.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("debes ingresar un nombre de usuario", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("debes ingresar una contraseña", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("nombre de usuario y/o contraseña invalidos", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        # Return apology if username input is blank
        username = request.form.get("username")
        if not username:
            return apology("debes ingresar un nombre de usuario")

        # Checking if username already exists in database
        if db.execute("SELECT id FROM users WHERE username = ?", username):
            return apology("nombre de usuario ya existe")

        # Gettin the password
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # In case either field is blank
        if not password or not confirmation:
            return apology("debes ingresar una contraseña y/o su confirmación")

        # Checking if password complies with the criteria
        elif not is_valid(password):
            return apology("la contraseña debe ser de mínimo 5 caracteres y debe contener 1 letra en mayúscula, otra en minúscula, por lo menos un carácter especial (!#$%, etc) y un número")

        # In case passwords don't match
        elif password != confirmation:
            return apology("las contraseñas no coinciden")

        # Adding data to database
        db.execute("INSERT INTO users (username, hash) VALUES (?,?);",
                   username, generate_password_hash(password))
        flash("¡Ya estás registrado!")
        return redirect("/login")

    else:
        return render_template("register.html")


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """Change password and add founds"""

    if request.method == "POST":
        # Checking if the resquest was to change the password or for adding founds
        if request.form.get("id") == "password":
            old_password = request.form.get("old_password")
            password = request.form.get("password")
            confirmation = request.form.get("confirmation")

            # Checking if inputs are valid

            # Ensure inputs are not blank
            if not old_password or not password or not confirmation:
                return apology("debes ingresar la contraseña anterior, la nueva contraseña y confirmarla")

            # Query database for username
            rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

            # Ensure password is correct
            if not check_password_hash(rows[0]["hash"], old_password):
                return apology("contraseña incorrecta")

            # Checking if password complies with the criteria
            elif not is_valid(password):
                return apology("la contraseña debe ser de mínimo 5 caracteres y debe contener 1 letra en mayúscula, otra en minúscula, por lo menos un carácter especial (!#$%, etc) y un número")

            # Ensure passwords match
            elif password != confirmation:
                return apology("las contraseñas no coinciden")

            # Updating password in database
            db.execute("UPDATE users SET hash = ? WHERE id = ?;",
                       generate_password_hash(password), session["user_id"])

            return redirect("/")

    else:

        return render_template("account.html")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Index."""

    user = db.execute("SELECT * FROM users WHERE id = ?;", session["user_id"])[0]
    return render_template("index.html", user=user)


@app.route("/clients")
@login_required
def clients():
    """Display company clients"""

    clients = db.execute(
        "SELECT dog_clients.id, dog_clients.dog_name, human_clients.human_name, human_clients.phone_number FROM dog_clients JOIN human_clients ON dog_clients.human_id = human_clients.id;")
    humans = db.execute("SELECT * FROM human_clients;")
    return render_template("clients.html", clients=clients, humans=humans)


@app.route("/users", methods=["GET", "POST"])
@login_required
def users():
    """Get client history."""

    if request.method == "POST":
        dog_name = request.form.get("dog_name").upper()
        # Checking for blank inputs
        if not dog_name:
            return apology("debes ingresar el nombre de un peludo")

        human_name = request.form.get("human_name").upper()
        # Checking for blank inputs
        if not human_name:
            return apology("debes ingresar el nombre del tutor del peludo")

        # Getting the ID's
        human_id = db.execute("SELECT id FROM human_clients WHERE human_name = ?;", human_name)
        # Checking if human exists in db
        if not human_id:
            return apology("ese tutor no existe en nuestra base de datos")
        else:
            human_id = int(db.execute(
                "SELECT id FROM human_clients WHERE human_name = ?;", human_name)[0]["id"])

        dog_id = db.execute(
            "SELECT id FROM dog_clients WHERE dog_name = ? AND human_id = ?;", dog_name, human_id)
        # Checking if dog exists in db
        if not dog_id:
            return apology("el peludo que buscas no existe en la base datos, si quieres puedes crearlo")
        else:
            dog_id = int(db.execute(
                "SELECT id FROM dog_clients WHERE dog_name = ? AND human_id = ?;", dog_name, human_id)[0]["id"])

        # Get userd
        return get_userd(db, dog_id, human_id)

    else:
        return render_template("users.html")


@app.route("/create_dog", methods=["GET", "POST"])
@login_required
def create_dog():
    """Create a dog client profile"""
    if request.method == "POST":

        dog_id = request.form.get("dog_id").upper()
        # Checking for blank inputs
        if not dog_id:
            return apology("debes ingresar el ID del peludo a registrar")
        else:
            dog_id = int(request.form.get("dog_id").upper())

        dog_name = request.form.get("dog_name").upper()
        # Checking for blank inputs
        if not dog_name:
            return apology("debes ingresar el nombre del peludo a registrar")

        race = request.form.get("race")
        # Checking for blank inputs
        if not race:
            return apology("debes ingresar la raza del peludo a registrar")

        # Getting the race_id
        race_id = int(db.execute("SELECT id FROM races WHERE race_name = ?;", race)[0]["id"])

        human_name = request.form.get("human_name").upper()
        # Checking for blank inputs
        if not human_name:
            return apology("debes ingresar el nombre del tutor del peludo a registrar")

        # Getting the human_id
        human_id = db.execute("SELECT id FROM human_clients WHERE human_name = ?;", human_name)
        # Checking if human exists
        if not human_id:
            return apology("el tutor con ese nombre no existe")
        else:
            human_id = int(db.execute(
                "SELECT id FROM human_clients WHERE human_name = ?;", human_name)[0]["id"])

        # Getting the dog_image
        dog_image = request.files.get("dog_image")
        if not dog_image:
            return apology("debes adjuntar una imágen del peludo")
        elif not dog_image.mimetype.startswith("image/"):
            return apology("el archivo ingreasdo no es una imágen")
        else:
            mimetype = dog_image.mimetype
            image_data = dog_image.read()

        # Inserting dog into dog_clients db
        db.execute("INSERT INTO dog_clients (id, dog_name, race_id, human_id, dog_image, mimetype) VALUES (?, ?, ?, ?, ?, ?);",
                   dog_id, dog_name, race_id, human_id, image_data, mimetype)

        flash("¡Peludo registrado!")
        return get_userd(db, dog_id, human_id)

    else:
        races = db.execute("SELECT * FROM races;")
        return render_template("create_dog.html", races=races)


@app.route("/modify_dog", methods=["GET", "POST"])
@login_required
def modify_dog():
    """Modify a dog client profile"""

    if request.method == "POST":

        action = request.form.get("action")

        # Current data
        dog_name = request.form.get("dog_name").upper()
        # Checking for blank inputs
        if not dog_name:
            return apology("debes ingresar el nombre del peludo a modificar")

        human_name = request.form.get("human_name").upper()
        # Checking for blank inputs
        if not human_name:
            return apology("debes ingresar el nombre del tutor del peludo a modificar")

        # Getting the human_id
        human_id = db.execute("SELECT id FROM human_clients WHERE human_name = ?;", human_name)
        # Checking if human exists
        if not human_id:
            return apology("el tutor con ese nombre no existe")
        else:
            human_id = int(db.execute(
                "SELECT id FROM human_clients WHERE human_name = ?;", human_name)[0]["id"])

        # Getting the dog_id
        dog_id = db.execute(
            "SELECT id FROM dog_clients WHERE dog_name = ? AND human_id = ?;", dog_name, human_id)
        # Checking if dog exists
        if not dog_id:
            return apology("el peludo con ese nombre y/o tutor no existe")
        else:
            dog_id = int(db.execute(
                "SELECT id FROM dog_clients WHERE dog_name = ? AND human_id = ?;", dog_name, human_id)[0]["id"])

        # Handling edition
        if action == "edit":
            # New data
            # Dog
            new_dog_id = request.form.get("new_dog_id")
            if not new_dog_id:
                new_dog_id = dog_id
            else:
                # Check if new ID inserted already exists in the db
                if db.execute("SELECT * FROM dog_clients WHERE id = ?;", int(new_dog_id)):
                    return apology("ese ID ya está en la base de datos")
                else:
                    new_dog_id = int(new_dog_id)

            new_dog_name = request.form.get("new_dog_name").upper()
            if not new_dog_name:
                new_dog_name = dog_name

            # human
            new_human_name = request.form.get("new_human_name").upper()
            if not new_human_name:
                new_human_name = human_name
                new_human_id = human_id
            else:
                # Getting the new_human_id
                new_human_id = db.execute(
                    "SELECT id FROM human_clients WHERE human_name = ?;", new_human_name)
                # Checking if human exists
                if not new_human_id:
                    return apology("el tutor nuevo con ese nombre no existe")
                else:
                    new_human_id = int(db.execute(
                        "SELECT id FROM human_clients WHERE human_name = ?;", new_human_name)[0]["id"])

            # Race
            race = request.form.get("race")
            # Checking for blank inputs
            if not race:
                race_id = int(db.execute(
                    "SELECT race_id FROM dog_clients WHERE id = ?;", dog_id)[0]["race_id"])
            else:
                race_id = int(db.execute(
                    "SELECT id FROM races WHERE race_name = ?;", race)[0]["id"])

            # Image
            new_dog_image = request.files.get("new_dog_image")
            if not new_dog_image:
                new_image_data = db.execute("SELECT dog_image FROM dog_clients WHERE id = ?;", dog_id)[
                    0]["dog_image"]
                new_mimetype = db.execute("SELECT mimetype FROM dog_clients WHERE id = ?;", dog_id)[
                    0]["mimetype"]
            elif not new_dog_image.mimetype.startswith("image/"):
                return apology("el archivo ingreasdo no es una imágen")
            else:
                new_mimetype = new_dog_image.mimetype
                new_image_data = new_dog_image.read()

            # Updating data in database
            db.execute("UPDATE dog_clients SET id = ?, dog_name = ?, race_id = ?, human_id = ?, dog_image = ?, mimetype = ? WHERE id = ?;",
                       new_dog_id, new_dog_name, race_id, new_human_id, new_image_data, new_mimetype, dog_id)

            flash("¡Peludo modificado!")
            return redirect("/clients")

        # Handling deletion
        elif action == "delete":

            # Deleting data in database
            db.execute("DELETE FROM dog_clients WHERE id = ?;", dog_id)

            flash("¡Peludo eliminado!")
            return redirect("/users")

    else:
        races = db.execute("SELECT * FROM races;")
        return render_template("modify_dog.html", races=races)


@app.route("/create_human", methods=["GET", "POST"])
@login_required
def create_human():
    """Create a human client profile"""
    if request.method == "POST":
        human_name = request.form.get("human_name").upper()
        # Checking for blank inputs
        if not human_name:
            return apology("debes ingresar el nombre del tutor a registrar")

        phone_number = request.form.get("phone_number")
        # Checking for blank inputs
        if not phone_number:
            return apology("debes ingresar el número de teléfono del tutor")

        human = db.execute("SELECT human_name FROM human_clients WHERE human_name = ?;", human_name)
        # Checking if human already exists in db
        if human:
            return apology("ese nombre de tutor ya existe")

        # Inserting human into human_clients db
        db.execute("INSERT INTO human_clients (human_name, phone_number) VALUES (?, ?);",
                   human_name, phone_number)

        flash("¡Tutor registrado!")
        return redirect("/create_dog")

    else:
        return render_template("create_human.html")


@app.route("/modify_human", methods=["GET", "POST"])
@login_required
def modify_human():
    """Modify a human client profile"""
    if request.method == "POST":

        action = request.form.get("action")

        # Current data
        human_name = request.form.get("human_name").upper()
        # Checking for blank inputs
        if not human_name:
            return apology("debes ingresar el nombre del tutor a modificar")

        # Getting the human_id
        human_id = db.execute("SELECT id FROM human_clients WHERE human_name = ?;", human_name)
        # Checking if human exists
        if not human_id:
            return apology("el tutor con ese nombre no existe")
        else:
            human_id = int(db.execute(
                "SELECT id FROM human_clients WHERE human_name = ?;", human_name)[0]["id"])

        phone_number = request.form.get("phone_number").upper()
        # Checking for blank inputs
        if not phone_number:
            return apology("debes ingresar el nombre del tutor del peludo a modificar")

        # Handling edition
        if action == "edit":
            # New data
            # human
            new_human_name = request.form.get("new_human_name").upper()
            if not new_human_name:
                new_human_name = human_name

            # phone_number
            new_phone_number = request.form.get("new_phone_number").upper()
            if not new_phone_number:
                new_phone_number = phone_number

            # Updating data in database
            db.execute("UPDATE human_clients SET human_name = ?, phone_number = ? WHERE id = ?;",
                       new_human_name, new_phone_number, human_id)

            flash("¡Tutor modificado!")
            return redirect("/clients")

        # Handling deletion
        elif action == "delete":

            # Check if client has a dog associated to him
            if db.execute("SELECT * FROM dog_clients WHERE human_id = ?;", human_id):
                return apology("Este tutor tiene peludos asociados a él. No se puede eliminar un tutor con peludos")
            # Deleting data in database
            db.execute("DELETE FROM human_clients WHERE id = ?;", human_id)

            flash("¡Tutor eliminado!")
            return redirect("/clients")

    else:
        return render_template("modify_human.html")


@app.route("/create_race", methods=["GET", "POST"])
@login_required
def create_race():
    """Create a dog client profile"""
    if request.method == "POST":
        race_name = request.form.get("race_name").upper()
        # Checking for blank inputs
        if not race_name:
            return apology("debes ingresar el nombre de la raza a crear")

        # In case race already exist in db
        if db.execute("SELECT * FROM races WHERE race_name = ?;", race_name):
            return apology("esta raza ya existe en nuestra base de datos")

        # Inserting race into races db
        db.execute("INSERT INTO races (race_name) VALUES (?);", race_name)

        flash("¡Raza creada!")
        return redirect("/clients")

    else:
        races = db.execute("SELECT * FROM races;")
        return render_template("create_race.html", races=races)


@app.route("/courses")
@login_required
def courses():
    """Display courses"""

    courses = db.execute("SELECT * FROM courses;")
    return render_template("courses.html", courses=courses)


@app.route("/create_course", methods=["GET", "POST"])
@login_required
def create_course():
    """Create a generic course"""

    if request.method == "POST":
        course_name = request.form.get("course_name").upper()
        # Checking for blank inputs
        if not course_name:
            return apology("debes ingresar el nombre del curso a crear")

        # In case course already exist in db
        if db.execute("SELECT * FROM courses WHERE course_name = ?;", course_name):
            return apology("este curso ya existe en nuestra base de datos")

        # Inserting course into courses db
        db.execute("INSERT INTO courses (course_name) VALUES (?);", course_name)

        flash("¡Curso creado!")
        return redirect("/courses")

    else:
        courses = db.execute("SELECT * FROM courses;")
        return render_template("create_course.html", courses=courses)


@app.route("/modify_course", methods=["GET", "POST"])
@login_required
def modify_course():
    """Modify a generic course"""
    if request.method == "POST":

        action = request.form.get("action")
        # Current data
        course_name = request.form.get("course_name").upper()
        # Checking for blank inputs
        if not course_name:
            return apology("debes ingresar el nombre del curso a modificar")

        # Getting the course id
        course_id = db.execute("SELECT id FROM courses WHERE course_name = ?;", course_name)
        # Checking if course exists
        if not course_id:
            return apology("el curso con ese nombre no existe")
        else:
            course_id = int(db.execute(
                "SELECT id FROM courses WHERE course_name = ?;", course_name)[0]["id"])

        # Manage edition
        if action == "edit":

            # New data
            # course
            new_course_name = request.form.get("new_course_name").upper()
            if not new_course_name:
                new_course_name = course_name

            # Updating data in database
            db.execute("UPDATE courses SET course_name = ? WHERE id = ?;",
                       new_course_name, course_id)

            flash("¡Curso modificado!")
            return redirect("/courses")

        # Manage edition
        elif action == "delete":

            if db.execute("SELECT * FROM courses WHERE id = ?;", course_id):
                return apology("no se puede crear curso ya que tiene sesiones asociadas a él")

            # Updating data in database
            db.execute("DELETE FROM courses WHERE id = ?;", course_id)

            flash("¡Curso eliminado!")
            return redirect("/courses")

    else:
        courses = db.execute("SELECT * FROM courses;")
        return render_template("modify_course.html", courses=courses)


@app.route("/create_session", methods=["GET", "POST"])
@login_required
def create_session():
    """Create a dog session"""
    if request.method == "POST":

        human_name = request.form.get("human_name").upper()
        # Checking for blank inputs
        if not human_name:
            return apology("debes ingresar el nombre del tutor del peludo")

        # Getting the human_id
        human_id = db.execute("SELECT id FROM human_clients WHERE human_name = ?;", human_name)
        # Checking if human exists
        if not human_id:
            return apology("el tutor con ese nombre no existe")
        else:
            human_id = int(db.execute(
                "SELECT id FROM human_clients WHERE human_name = ?;", human_name)[0]["id"])

        dog_name = request.form.get("dog_name").upper()
        # Checking for blank inputs
        if not dog_name:
            return apology("debes ingresar el nombre del peludo")

        # Getting the dog_id
        dog_id = db.execute(
            "SELECT id FROM dog_clients WHERE dog_name = ? AND human_id = ?;", dog_name, human_id)
        # Checking if dog exists
        if not dog_id:
            return apology("el peludo para ese tutor con ese nombre no existe")
        else:
            dog_id = int(db.execute(
                "SELECT id FROM dog_clients WHERE dog_name = ? AND human_id = ?;", dog_name, human_id)[0]["id"])

        course = request.form.get("course")
        if not course:
            return apology("debes ingresar el curso al que pertenece la sesión")

        course_id = int(db.execute(
            "SELECT id FROM courses WHERE course_name = ?;", course)[0]["id"])

        description = request.form.get("description")
        # Checking for blank inputs
        if not description:
            return apology("debes ingresar la descripción")

        status = request.form.get("status")
        # Checking for blank inputs
        if not status:
            return apology("debes ingresar el estado del curso")

        level = request.form.get("level")
        # Checking for blank inputs
        if not level:
            return apology("debes ingresar el nivel de la sesión")

        # Inserting session into sessions db
        db.execute("INSERT INTO sessions (dog_id, human_id, course_id, description, status, level) VALUES (?, ?, ?, ?, ?, ?);",
                   dog_id, human_id, course_id, description, status, level)

        # Updating all sessions related to user and course id to current status
        db.execute("UPDATE sessions SET status = ? WHERE dog_id = ? AND human_id = ? AND course_id = ?;",
                   status, dog_id, human_id, course_id)

        flash("¡Sesión agregada!")
        return get_userd(db, dog_id, human_id)

    else:
        courses = db.execute("SELECT * FROM courses;")
        return render_template("create_session.html", courses=courses)


@app.route("/edit_session/<int:session_id>", methods=["GET", "POST"])
@login_required
def edit_session(session_id):
    """Edits a specific dog session"""

    # Initializing database with session_id
    session = db.execute("SELECT * FROM sessions WHERE id = ?;", session_id)[0]

    if request.method == "POST":

        action = request.form.get("action")

        # Manage edition
        if action == "edit":

            human_name = request.form.get("human_name").upper()
            # Checking for blank inputs
            if not human_name:
                return apology("debes ingresar el nombre del tutor del peludo")

            # Getting the human_id
            human_id = db.execute("SELECT id FROM human_clients WHERE human_name = ?;", human_name)
            # Checking if human exists
            if not human_id:
                return apology("el tutor con ese nombre no existe")
            else:
                human_id = int(db.execute(
                    "SELECT id FROM human_clients WHERE human_name = ?;", human_name)[0]["id"])

            dog_name = request.form.get("dog_name").upper()
            # Checking for blank inputs
            if not dog_name:
                return apology("debes ingresar el nombre del peludo")

            # Getting the dog_id
            dog_id = db.execute(
                "SELECT id FROM dog_clients WHERE dog_name = ? AND human_id = ?;", dog_name, human_id)
            # Checking if dog exists
            if not dog_id:
                return apology("el peludo para ese tutor con ese nombre no existe")
            else:
                dog_id = int(db.execute(
                    "SELECT id FROM dog_clients WHERE dog_name = ? AND human_id = ?;", dog_name, human_id)[0]["id"])

            course = request.form.get("course")
            if not course:
                return apology("debes ingresar el curso al que pertenece la sesión")

            course_id = int(db.execute(
                "SELECT id FROM courses WHERE course_name = ?;", course)[0]["id"])

            description = request.form.get("description")
            # Checking for blank inputs
            if not description:
                return apology("debes ingresar la descripción")

            status = request.form.get("status")
            # Checking for blank inputs
            if not status:
                return apology("debes ingresar el estado del curso")

            level = request.form.get("level")
            # Checking for blank inputs
            if not level:
                return apology("debes ingresar el nivel de la sesión")

            # Inserting session into sessions db
            db.execute("UPDATE sessions SET dog_id = ?, human_id = ?, course_id = ?, description = ?, status = ?, level = ? WHERE id = ? AND dog_id = ? AND human_id = ? AND course_id = ?;",
                       dog_id, human_id, course_id, description, status, level, session["id"], session["dog_id"], session["human_id"], session["course_id"])

            # Updating all sessions related to user and course id to current status
            db.execute("UPDATE sessions SET status = ? WHERE dog_id = ? AND human_id = ? AND course_id = ?;",
                       status, dog_id, human_id, course_id)

            flash("¡Sesión editada!")

            # Go to userd page
            return get_userd(db, session["dog_id"], session["human_id"])

        # Manage deletion
        elif action == "delete":

            # Deleting session in sessions db
            db.execute("DELETE FROM sessions WHERE id = ?;", session["id"])

            flash("¡Sesión eliminada!")

            # Go to userd page
            return get_userd(db, session["dog_id"], session["human_id"])

    else:

        dog = db.execute("SELECT * FROM dog_clients WHERE id = ?;", session["dog_id"])[0]
        human = db.execute("SELECT * FROM human_clients WHERE id = ?;", session["human_id"])[0]
        i_course = db.execute("SELECT * FROM courses WHERE id = ?;", session["course_id"])[0]
        description = session["description"]
        status = session["status"]
        level = session["level"]
        courses = db.execute("SELECT * FROM courses;")
        return render_template("edit_session.html", session=session, dog=dog, human=human, i_course=i_course, description=description, status=status, level=level, courses=courses)


@app.route("/modify_c_courses/<int:course_id>", methods=["GET", "POST"])
@login_required
def modify_c_course(course_id):
    """Modifies a specific dog course status"""

    # Initializing database with session_id
    session = db.execute("SELECT * FROM sessions WHERE id = ?;", course_id)[0]

    if request.method == "POST":

        course = request.form.get("course")
        if not course:
            return apology("debes ingresar el curso al que pertenece la sesión")

        status = request.form.get("status")
        # Checking for blank inputs
        if not status:
            return apology("debes ingresar el estado del curso")

        # Updating all sessions related to user and course id to current status
        db.execute("UPDATE sessions SET status = ? WHERE dog_id = ? AND human_id = ? AND course_id = ?;",
                   status, session["dog_id"], session["human_id"], session["course_id"])

        flash("¡Estado del curso modificado!")

        # Go to userd page
        return get_userd(db, session["dog_id"], session["human_id"])

    else:

        i_course = db.execute("SELECT * FROM courses WHERE id = ?;", session["course_id"])[0]
        status = session["status"]
        return render_template("modify_c_course.html", session=session, course=i_course, status=status, id=course_id)


@app.route("/api/dogs")
@login_required
def get_dogs():
    dogs = db.execute("SELECT id, dog_name, race_id, human_id FROM dog_clients;")
    return jsonify(dogs)


@app.route("/api/humans/<dog_id>")
@login_required
def get_humans(dog_id):
    humans = db.execute(
        "SELECT human_name FROM human_clients WHERE id IN (SELECT human_id FROM dog_clients WHERE id = ?);", dog_id)
    return jsonify(humans)


@app.route("/api/human")
@login_required
def get_human():
    human = db.execute("SELECT human_name FROM human_clients;")
    return jsonify(human)


@app.route("/api/dogId/<dog_id>")
@login_required
def get_dog_id(dog_id):
    id = db.execute("SELECT id FROM dog_clients WHERE id = ?;", dog_id)
    return jsonify(id)
