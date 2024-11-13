import base64
import requests

from flask import redirect, render_template, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def is_valid(password):
    # Password must be 5 chars long and at least contain:
    # 1 special char, 1 upper letter, 1 lowercase letter, 1 number.
    sc = False
    ul = False
    ll = False
    n = False

    if len(password) >= 5:
        for char in password:
            if not sc or not ul or not ll or not n:
                if not char.isalnum():
                    sc = True
                if char.isupper():
                    ul = True
                if char.islower():
                    ll = True
                if char.isnumeric():
                    n = True
            else:
                return True
    return sc and ul and ll and n

def get_userd(db, dog_id, human_id):

        image = db.execute("SELECT * FROM dog_clients WHERE id = ? AND human_id = ?;", dog_id, human_id)[0]
        enc_image = base64.b64encode(image["dog_image"]).decode("utf-8")
        mimetype = image["mimetype"]

        # Check sessions and courses related to dog and human
        sessions = db.execute("SELECT * FROM sessions WHERE dog_id = ? AND human_id = ?;", dog_id, human_id)
        courses = db.execute("SELECT courses.course_name, sessions.id, sessions.course_id, sessions.status FROM courses JOIN sessions ON courses.id = sessions.course_id WHERE sessions.dog_id = ? AND sessions.human_id = ? GROUP BY courses.id;", dog_id, human_id)

        dog_name = db.execute("SELECT dog_name FROM dog_clients WHERE id = ?;", dog_id)[0]["dog_name"]
        human_name = db.execute("SELECT human_name FROM human_clients WHERE id = ?;", human_id)[0]["human_name"]

        return render_template("/userd.html", sessions=sessions, courses=courses, dog=dog_name, human=human_name, image=enc_image, mimetype=mimetype)
