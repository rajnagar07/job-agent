from database.db import SessionLocal
from database.models import User
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from auth.token_service import (
    verify_token,
    delete_token,
    VERIFY_EMAIL
)

from auth.service import (
    register_user,
    login_user
)

auth_bp = Blueprint(
    "auth",
    __name__
)


# -----------------------------------
# Signup
# -----------------------------------

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")

        success, message = register_user(
            name=name,
            email=email,
            phone=phone,
            password=password
        )

        flash(message)

        if success:
            return redirect(url_for("auth.login"))

    return render_template("signup.html")


# -----------------------------------
# Login
# -----------------------------------

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        success, message, user = login_user(
            username=username,
            password=password
        )

        if success:

            session["user_id"] = user.id
            session["user_name"] = user.name

            flash(message)

            return redirect(url_for("index"))

        flash(message)

    return render_template("login.html")


@auth_bp.route("/verify-email/<token>")
def verify_email(token):

    user_token = verify_token(token, VERIFY_EMAIL)

    if not user_token:
        flash("Verification link is invalid or expired.")
        return redirect(url_for("auth.login"))

    session = SessionLocal()

    try:
        user = session.get(User, user_token.user_id)

        if user:
            user.email_verified = True
            session.commit()

    finally:
        session.close()

    delete_token(token)

    flash("Email verified successfully. Please login.")

    return redirect(url_for("auth.login"))
# -----------------------------------
# Logout
# -----------------------------------

@auth_bp.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully.")

    return redirect(url_for("auth.login"))