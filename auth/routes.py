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
    login_user,forgot_password, 
    reset_password,
    resend_verification_email
)
# from auth.service import forgot_password, reset_password, resend_verification_email


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

            # Redirect back to the page the user originally wanted
            next_page = request.args.get("next")

            if next_page:
                return redirect(next_page)

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
# forget password
# -----------------------------------

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password_route():

    if request.method == "POST":

        email = request.form.get("email")

        success, message = forgot_password(email)

        flash(message)

        if success:
            return redirect(url_for("auth.login"))

    return render_template("forgot_password.html")
# -----------------------------------
# Logout
# -----------------------------------

@auth_bp.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully.")

    return redirect(url_for("auth.login"))


@auth_bp.route(
    "/reset-password/<token>",
    methods=["GET", "POST"]
)
def reset_password_route(token):

    if request.method == "POST":

        password = request.form.get("password")
        confirm = request.form.get("confirm_password")

        if password != confirm:

            flash("Passwords do not match.")

            return render_template(
                "reset_password.html",
                token=token
            )

        success, message = reset_password(
            token,
            password
        )

        flash(message)

        if success:
            return redirect(url_for("auth.login"))

    return render_template(
        "reset_password.html",
        token=token
    )


@auth_bp.route(
    "/resend-verification",
    methods=["GET", "POST"]
)
def resend_verification():

    if request.method == "POST":

        email = request.form.get("email")

        success, message = resend_verification_email(
            email
        )

        flash(
            message,
            "success" if success else "danger"
        )

        if success:
            return redirect(
                url_for("auth.login")
            )

    return render_template(
        "resend_verification.html"
    )
