import os

import resend

from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

FROM_EMAIL = os.getenv(
    "FROM_EMAIL",
    "AI Job Agent <onboarding@resend.dev>"
)

APP_URL = os.getenv(
    "APP_URL",
    "http://127.0.0.1:5000"
)


# ======================================================
# Generic Email Sender
# ======================================================

def send_email(to_email, subject, html):

    try:

        params = {
            "from": FROM_EMAIL,
            "to": [to_email],
            "subject": subject,
            "html": html,
        }

        resend.Emails.send(params)

        return True

    except Exception as e:

        print("Email Error:", e)

        return False


# ======================================================
# Verification Email
# ======================================================

def send_verification_email(user, token):

    verify_link = (
        f"{APP_URL}/verify-email/{token}"
    )

    html = f"""
    <h2>Welcome to AI Job Agent 👋</h2>

    <p>
        Thank you for signing up.
    </p>

    <p>
        Please verify your email by clicking below.
    </p>

    <p>
        <a href="{verify_link}">
            Verify Email
        </a>
    </p>

    <p>
        If you didn't create this account,
        you can safely ignore this email.
    </p>
    """

    return send_email(
        user.email,
        "Verify your email",
        html
    )


# ======================================================
# Forgot Password Email
# ======================================================

def send_password_reset_email(user, token):

    reset_link = (
        f"{APP_URL}/reset-password/{token}"
    )

    html = f"""
    <h2>Password Reset</h2>

    <p>
        Click the button below to reset your password.
    </p>

    <p>
        <a href="{reset_link}">
            Reset Password
        </a>
    </p>

    <p>
        If you didn't request this,
        simply ignore this email.
    </p>
    """

    return send_email(
        user.email,
        "Reset your password",
        html
    )