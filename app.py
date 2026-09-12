from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3 
from functools import wraps
import os


#Flask app function & sqlite3 connection

app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY") 

def get_db_connection():
    connection = sqlite3.connect("harbor.db")

    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def initialize_database():

    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone_number TEXT,
            password_hash TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS service_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER,

            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            customer_phone TEXT,

            preferred_contact TEXT,

            service_type TEXT NOT NULL,
            urgency TEXT,

            address TEXT,
            zip_code TEXT,

            description TEXT NOT NULL,

            preferred_date TEXT,
            preferred_time TEXT,

            status TEXT NOT NULL DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    connection.commit()
    connection.close()

def login_required(view_function):

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("login"))

        return view_function(*args, **kwargs)

    return wrapped_view

#-----------------------------------------------------------
#HOME
#-----------------------------------------------------------


@app.route("/")
def home():
    return render_template("index.html")

#-----------------------------------------------------------
#ABOUT
#-----------------------------------------------------------


@app.route("/about")
def about():
    return render_template("about.html")

#-----------------------------------------------------------
#SERVICES
#-----------------------------------------------------------


@app.route("/services")
def services():
    return render_template("services.html")

#-----------------------------------------------------------
#CONTACT
#-----------------------------------------------------------


@app.route("/contact", methods=["GET", "POST"])
def contact():

    # GET request:
    # just display the contact page and END the function here.
    if request.method == "GET":
        return render_template("contact.html")


    # If Python gets this far, the request MUST be POST.

    user_id = session.get("user_id")

    full_name = request.form.get("full-name")
    email = request.form.get("email")
    phone_number = request.form.get("phone-number")
    preffered_contact = request.form.get("preffered-contact")

    service_type = request.form.get("service-type")
    urgency = request.form.get("urgency")
    address = request.form.get("address")
    zip_code = request.form.get("zip-code")
    description = request.form.get("problem-description")

    preffered_date = request.form.get("preffered-date")
    preffered_time = request.form.get("preffered-time")


    # Server-side validation

    if not full_name:
        return render_template(
            "contact.html",
            form_error="Full name is required."
        )

    if not email:
        return render_template(
            "contact.html",
            form_error="Email is required."
        )

    if not service_type or service_type == "empty-placeholder":
        return render_template(
            "contact.html",
            form_error="Please select a service type."
        )

    if not description:
        return render_template(
            "contact.html",
            form_error="Please describe the problem."
        )


    # Database INSERT

    connection = get_db_connection()

    cursor = connection.execute(
        """
        INSERT INTO service_requests (
            user_id,
            customer_name,
            customer_email,
            customer_phone,
            preferred_contact,
            service_type,
            urgency,
            address,
            zip_code,
            description,
            preferred_date,
            preferred_time
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            full_name,
            email,
            phone_number,
            preffered_contact,
            service_type,
            urgency,
            address,
            zip_code,
            description,
            preffered_date,
            preffered_time
        )
    )

    request_id = cursor.lastrowid

    connection.commit()
    connection.close()


    # Authenticated customer
    if user_id is not None:
        return redirect(url_for("dashboard"))


    # Guest customer
    return redirect(
        url_for(
            "request_confirmation",
            request_id=request_id
        )
    )


#-----------------------------------------------------------
#FAQ
#-----------------------------------------------------------


@app.route("/faq")
def faq():
    return render_template("faq.html")

#-----------------------------------------------------------
#PRIVACY
#-----------------------------------------------------------


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


#-----------------------------------------------------------
#REGISTER
#-----------------------------------------------------------


@app.route("/register", methods=["Get", "Post"])
def register():

    if request.method == "POST":

        full_name = request.form.get("fullName")
        email = request.form.get("email")
        phone_number = request.form.get("phonenumber")
        password = request.form.get("password")
        confirm_password = request.form.get("confirmPassword")

        #Server Side validation

        if not full_name:
            return render_template("register.html")

        if not email:
            return render_template("register.html")

        if not password:
            return render_template("register.html")

        if len(password) < 12:
            return render_template("register.html")

        if password != confirm_password:
            return render_template("register.html")

        #server hash

        password_hash = generate_password_hash(password)

        connection = get_db_connection()

        try:
            connection.execute(
                """
                INSERT INTO users (full_name, email, phone_number, password_hash)
                VALUES (?, ?, ?, ?)
                """,
                (full_name, email, phone_number, password_hash)
            )

            connection.commit()
            
        except sqlite3.IntegrityError:
            return render_template(
                "register.html",
                email_error="An account with that email already exists.",
                full_name=full_name,
                email=email,
                phone_number=phone_number
            )

        finally:
            connection.close()

        return redirect(url_for("login"))

    return render_template("register.html")

#-----------------------------------------------------------
#LOGIN
#-----------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        connection = get_db_connection()

        user = connection.execute(
            """
            SELECT id, full_name, email, password_hash
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        connection.close()

        if user is None:

            return render_template(
                "login.html",
                login_error="Invalid email or password"
            )


        password_is_valid = check_password_hash(
            user[3],
            password
        )

        if password_is_valid:

            session["user_id"] = user[0]

            return redirect(url_for("dashboard"))

        else:
            return render_template(
                "login.html",
                login_error="Invalid email or password."
            )

        

    return render_template("login.html")


#---------------------------------------------------------
#session_logout
#---------------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


#---------------------------------------------------------
#/dashboard
#---------------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():

    user_id = session["user_id"]

    connection = get_db_connection()

    user = connection.execute(
        """
        SELECT id, full_name, email, phone_number
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    requests = connection.execute(
        """
        SELECT
            id,
            service_type,
            status,
            urgency,
            preferred_date,
            preferred_time,
            created_at
        FROM service_requests
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 5
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    return render_template(
        "dashboard.html",
        user_name=user[1],
        user_email=user[2],
        user_phone=user[3],
        service_requests=requests
    )

#---------------------------------------------------------
#/request-confirmation
#---------------------------------------------------------


@app.route("/request-confirmation/<int:request_id>")
def request_confirmation(request_id):

    return render_template(
        "request-confirmation.html",
        request_id=request_id
    )


#---------------------------------------------------------
#/my_requests
#---------------------------------------------------------

@app.route("/my-requests")
@login_required
def my_requests():

    user_id = session["user_id"]

    connection = get_db_connection()

    requests = connection.execute(
        """
        SELECT
            id,
            service_type,
            status,
            urgency,
            preferred_date,
            preferred_time,
            created_at
        FROM service_requests
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    return render_template(
        "my-requests.html",
        service_requests=requests
    )

#---------------------------------------------------------
#/request-details
#---------------------------------------------------------

@app.route("/my-request/<int:request_id>")
@login_required
def request_details(request_id):

    user_id = session["user_id"]

    connection = get_db_connection()

    service_request = connection.execute(
        """
        SELECT
            id,
            service_type,
            status,
            urgency,
            address,
            zip_code,
            description,
            preferred_date,
            preferred_time,
            created_at
        FROM service_requests
        WHERE id = ?
        AND user_id = ?
        """,
        (request_id, user_id)
    ).fetchone()

    connection.close()

    if service_request is None:
        return "SERVICE REQUEST NOT FOUND", 404

    return render_template(
        "request-details.html",
        service_request=service_request
    )

#---------------------------------------------------------
#/account settings
#---------------------------------------------------------

@app.route("/account-settings", methods=["GET", "POST"])
@login_required
def account_settings():

    user_id = session["user_id"]

    connection = get_db_connection()

    errors = {}

    profile_success = None
    password_success = None


    # HANDLE ACCOUNT SETTINGS FORMS

    if request.method == "POST":

        action = request.form.get("action")


        # UPDATE PERSONAL INFORMATION

        if action == "update_profile":

            full_name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip().lower()
            phone_number = request.form.get("phone_number", "").strip()


            # Required field validation

            if not full_name:
                errors["full_name"] = "Full name is required."

            if not email:
                    errors["email"] = "Email is required."

            #Legnth Validation

            if len(full_name) > 100:
                errors["full_name"] = "Full name is too long."

            if len(email) > 254:
                errors["email"] = "Email is too long."

            if len(phone_number) > 30:
                errors["phone_number"] = "Phone number is too long."


            # Update user information

            if not errors:

                try:

                    connection.execute(
                        """
                        UPDATE users
                        SET
                            full_name = ?,
                            email = ?,
                            phone_number = ?
                        WHERE id = ?
                        """,
                        (full_name, email, phone_number, user_id)
                    )

                    connection.commit()

                    profile_success = "Your personal information has been successfully updated! "

                except sqlite3.IntegrityError:

                    errors["email"] = "An account with that email already exists."

        # CHANGE PASSWORD

        elif action == "change_password":

            current_password = request.form.get("current_password")
            new_password = request.form.get("new_password")
            confirm_password = request.form.get("confirm_password")

            if not current_password:
                errors["current_password"] = "Current password is required."

            if not new_password:
                    errors["new_password"] = "New password is required."

            if new_password != confirm_password:
                errors["confirm_password"] = "New passwords do not match."

            if not errors:


                user_password = connection.execute(
                    """
                    SELECT password_hash
                    FROM users
                    WHERE id = ?
                    """,
                    (user_id,)
                ).fetchone()

                if not check_password_hash(
                    user_password[0],
                    current_password
                ):
                    errors["current_password"] = "Current password is incorrect."

            if new_password:

                if len(new_password) < 12:
                    errors["new_password"] = "Password must be at least 12 characters long."

                elif len(new_password) > 128:
                    errors["new_password"] = "Password is too long."

                if not errors:

                    if check_password_hash(
                        user_password[0],
                        new_password
                    ):
                        errors["new_password"] = (
                            "New password must be different from your current password."
                        )

                if not errors:

                    new_password_hash = generate_password_hash(new_password)

                    connection.execute(
                        """
                        UPDATE users
                        SET password_hash = ?
                        WHERE id = ? 
                        """,
                        (new_password_hash, user_id)
                    )

                    connection.commit()

                    password_success = "Your password has been successfully changed!"

        elif action == "delete_account":

            delete_password = request.form.get("delete_password")

            if not delete_password:
                errors["delete_password"] = "Current password is required."

            if not errors:

                user_password = connection.execute(
                    """
                    SELECT password_hash
                    FROM users
                    WHERE id = ?
                    """,
                    (user_id,)
                ).fetchone()

                if not check_password_hash(
                    user_password[0],
                    delete_password
                ):
                    errors["delete_password"] = "Current password is incorrect"

            if not errors:

                try:

                    connection.execute(
                        """
                        UPDATE service_requests
                        SET user_id = NULL
                        WHERE user_id = ?
                        """,
                        (user_id,)
                    )

                    connection.execute(
                        """
                        DELETE FROM users
                        WHERE id = ?
                        """,
                        (user_id,)
                    )

                    connection.commit()

                    session.clear()

                    return redirect(url_for("home"))

                except sqlite3.Error:

                    connection.rollback()

                    errors["delete_account"] = (
                        "We are unable to delete your account. Please try again."
                    )
            


    # LOAD CURRENT USER INFORMATION

    user = connection.execute(
        """
        SELECT
            id,
            full_name,
            email,
            phone_number
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()

    connection.close()


    # DISPLAY ACCOUNT SETTINGS

    return render_template(
        "account-settings.html",
        user=user,
        errors=errors,
        profile_success=profile_success,
        password_success=password_success
    )

#---------------------------------------------------------
#/staff-login
#---------------------------------------------------------

@app.route("/staff-login", methods=["GET", "POST"])
def staff_login():

    return render_template("staff-login.html")

#Run server

if __name__=="__main__":

    initialize_database()

    app.run()