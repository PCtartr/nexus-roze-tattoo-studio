import os
import sqlite3
import time

from time import strftime
from time import localtime
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, execute_read_query, execute_write_query

# Configure application
app = Flask(__name__)

if __name__ == "__main__":
    # Access the variable Render already provides
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/account")
@login_required
def account():
    # fetch user info (including artist flag)
    user_data = execute_read_query(
        "SELECT username, phone_number, artist FROM users WHERE id = ?",
        (session["user_id"],)
    )

    # user_data[0] because fetchall returns a list of rows
    username = user_data[0]["username"]
    phone_number = user_data[0]["phone_number"]
    artist = user_data[0]["artist"]

    # fetch this user's scheduled tattoos
    tattoo_data = execute_read_query(
        "SELECT STRFTIME('%I:%M %p %m/%d/%Y', timestamp) AS timestamp, \
                tattoo_description, \
                STRFTIME('%I:%M %p %m/%d/%Y', scheduled_date) AS scheduled_date \
            FROM schedule WHERE user_id = ?",
        (session["user_id"],)
    )

    # build lists from tattoo_data rows
    timestamps = [row["timestamp"] for row in tattoo_data]
    descriptions = [row["tattoo_description"] for row in tattoo_data]
    scheduled_dates = [row["scheduled_date"] for row in tattoo_data]

    # if the user is an artist, also grab other artists' schedules (or whatever you need)
    artist_timestamps = []
    artist_descriptions = []
    artist_scheduled_dates = []
    if artist:
        artist_tattoo_data = execute_read_query(
            "SELECT STRFTIME('%I:%M %p %m/%d/%Y', timestamp) AS timestamp, \
                    tattoo_description,  \
                    STRFTIME('%I:%M %p %m/%d/%Y', scheduled_date) AS scheduled_date, \
                    (SELECT username FROM users WHERE id = schedule.user_id) AS client_name, \
                    (SELECT phone_number FROM users WHERE id = schedule.user_id) AS client_phone_number, \
                    schedule.user_id AS client_id \
                FROM schedule"
        )

        artist_timestamps = [row["timestamp"] for row in artist_tattoo_data]
        artist_descriptions = [row["tattoo_description"] for row in artist_tattoo_data]
        artist_scheduled_dates = [row["scheduled_date"] for row in artist_tattoo_data]
        artist_client_names = [row["client_name"] for row in artist_tattoo_data]
        artist_client_phone_numbers = [row["client_phone_number"] for row in artist_tattoo_data]
        artist_client_ids = [row["client_id"] for row in artist_tattoo_data]

        return render_template(
            "account.html",
            username=username,
            phone_number=phone_number,
            artist=artist,
            timestamps=timestamps,
            descriptions=descriptions,
            scheduled_dates=scheduled_dates,
            artist_timestamps=artist_timestamps,
            artist_descriptions=artist_descriptions,
            artist_scheduled_dates=artist_scheduled_dates,
            artist_client_names=artist_client_names,
            artist_client_phone_numbers=artist_client_phone_numbers,
            artist_client_ids=artist_client_ids
        )

    else:
        return render_template(
            "account.html",
            username=username,
            phone_number=phone_number,
            artist=artist, timestamps=timestamps,
            descriptions=descriptions,
            scheduled_dates=scheduled_dates
        )

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = execute_read_query(
            "SELECT * FROM users WHERE username = ?", (request.form.get("username"),)
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/account")

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
    # clear session for safety reasons
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("Username not entered", 400)
        elif not request.form.get("password"):
            return apology("Password not entered", 400)
        elif not request.form.get("confirmation"):
            return apology("Password confirmation not entered", 400)
        elif not request.form.get("phone_number"):
            return apology("Phone number not entered", 400)
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Password does not match confirmation", 400)

        # search for used username
        rows = execute_read_query("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))

        # search for existing usernames
        if len(rows) != 0:
            return apology("Username taken", 400)

        if request.form.get("artist") == "on":
            return render_template("artist_register.html", username=request.form.get("username"), phone_number=request.form.get("phone_number"), password=request.form.get("password"))

        # register new user
        # Wrap the variables in a tuple: (username, password_hash, phone_number)
        # Wrap the three values inside ONE pair of parentheses to make a single tuple
        # RIGHT: The SQL string is arg 1, the TUPLE of data is arg 2
        execute_write_query("INSERT INTO users (username, hash, phone_number, artist) VALUES (?, ?, ?, ?)", 
            (request.form.get("username"), generate_password_hash(request.form.get("password")), request.form.get("phone_number"), request.form.get("artist") == "on")
        )

        # pull new user info
        rows = execute_read_query("SELECT* FROM users WHERE username = ?", (request.form.get("username"),))

        # create session for user
        session["user_id"] = rows[0]["id"]

        # return to homepage
        return redirect("/account")
    else:
        return render_template("register.html")

@app.route("/booking", methods=["GET", "POST"])
@login_required
def booking():
    if request.method == "POST":
        # Get form data
        timestamp = datetime.now()  # Set execution time server-side
        tattoo_description = request.form.get("tattoo_description")
        scheduled_date = request.form.get("scheduled_date")

        # Insert into database
        execute_write_query(
            "INSERT INTO schedule (user_id, timestamp, tattoo_description, scheduled_date) VALUES (?, ?, ?, ?)",
            (session["user_id"], timestamp, tattoo_description, scheduled_date)
        )

        return redirect("/account")

    else:
        return render_template("booking.html")

@app.route("/gallery")
def gallery():
    return render_template("gallery.html")

@app.route("/pricing")
def pricing():
    return render_template("pricing.html")

@app.route("/delete_appointment", methods=["POST"])
@login_required
def delete_appointment():
    if request.method == "POST":
        return render_template(
            "delete.html",
            tattoo_description=request.form.get("tattoo_description"),
            client_id=request.form.get("client_id")
        )
    else:
        return redirect("/account")

@app.route("/delete_confirmed", methods=["POST"])
@login_required
def delete_confirmed():
    if request.method == "POST":
        # prefer client_id from the form when provided (artist deleting a client's appointment)
        client_id = request.form.get("client_id")
        tattoo_discription = request.form.get("tattoo_description")

        execute_write_query(
            "DELETE FROM schedule WHERE user_id = ? AND tattoo_description = ?",
            (client_id, tattoo_discription)
        )
        return redirect("/account")
    else:
        return redirect("/account")

@app.route("/artist_register", methods=["POST"])
def artist_register():
    if request.method == "POST":
        admin_username = request.form.get("admin_username")
        admin_password = request.form.get("admin_password")

        # Verify admin credentials (for simplicity, hardcoding here - in production, use a secure method)
        if admin_username == "admin" and admin_password == "adminpassword":  # Replace with secure check
            # Update the user's artist status in the database
            execute_write_query("INSERT INTO users (username, hash, phone_number, artist) VALUES (?, ?, ?, ?)", 
            (request.form.get("username"), generate_password_hash(request.form.get("password")), request.form.get("phone_number"), request.form.get("artist") == "on")
            )

            # pull new user info
            rows = execute_read_query("SELECT* FROM users WHERE username = ?", (request.form.get("username"),))

            # create session for user
            session["user_id"] = rows[0]["id"]

            # return to homepage
            return redirect("/account")
        else:
            return apology("Invalid admin credentials", 400)
    else:
        return redirect("/register")

@app.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    if request.method == "POST":
        return render_template("delete_account.html", username=request.form.get("username"))

@app.route("/delete_account_confirmed", methods=["POST"])
@login_required
def delete_account_confirmed():
    if request.method == "POST":
        user_id = session["user_id"]

        # Delete user from database
        execute_write_query("DELETE FROM schedule WHERE user_id = ?", (user_id,))
        execute_write_query("DELETE FROM users WHERE id = ?", (user_id,))

        # Clear session and redirect to homepage
        session.clear()
        return redirect("/")
    else:
        return redirect("/account")

@app.route("/delete_another_account", methods=["POST"])
@login_required
def delete_another_account():
    if request.method == "POST":
        return render_template("delete_another_account.html")
    else:
        return redirect("/account")

@app.route("/delete_another_account_search", methods=["POST"])
@login_required # Consider adding an additional admin check here to ensure only artists can delete other accounts
def delete_another_account_search():
    if request.method == "POST":
            admin_username = request.form.get("admin_username")
            admin_password = request.form.get("admin_password")
            if admin_username == "admin" and admin_password == "adminpassword":  # Replace with secure check
                users = execute_read_query("SELECT username, phone_number, artist FROM users")
                return render_template("delete_another_account_search.html", users=users)
            else:
                return apology("Invalid admin credentials", 400)
    else:
        return redirect("/account")

@app.route("/delete_account_from_search", methods=["POST"])
@login_required
def delete_account_from_search():
    if request.method == "POST":
        username = request.form.get("username")

        # Get the user_id first
        user_data = execute_read_query("SELECT id FROM users WHERE username = ?", (username,))
        if user_data:
            user_id = user_data[0]["id"]
            # Delete user from database
            execute_write_query("DELETE FROM schedule WHERE user_id = ?", (user_id,))
            execute_write_query("DELETE FROM users WHERE id = ?", (user_id,))

        # Clear session and redirect to homepage
        return redirect("/account")
    else:

        return redirect("/account")
