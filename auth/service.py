from database.db import SessionLocal
from database.models import User
from auth.token_service import (
    create_token,
    VERIFY_EMAIL
)

from auth.email_service import (
    send_verification_email
)

from auth.token_service import (
    create_token,
    RESET_PASSWORD
)

from auth.email_service import (
    send_password_reset_email
)

from auth.token_service import (
    verify_token,
    delete_token,
    RESET_PASSWORD
)

from auth.token_service import (
    create_token,
    VERIFY_EMAIL
)

from auth.email_service import (
    send_verification_email
)


# =====================================================
# Register User
# =====================================================

def register_user(name, email, phone, password):

    session = SessionLocal()

    try:

        # Clean input
        name = (name or "").strip()
        email = (email or "").strip().lower()
        phone = (phone or "").strip()

        # Required fields
        if not name:
            return False, "Name is required."

        if not password:
            return False, "Password is required."

        if len(password) < 8:
            return False, "Password must be at least 8 characters."

        # Email or phone required
        if not email and not phone:
            return False, "Please provide an email or phone number."

        # Check duplicate email
        if email:
            existing = (
                session.query(User)
                .filter_by(email=email)
                .first()
            )

            if existing:
                return False, "Email is already registered."

        # Check duplicate phone
        if phone:
            existing = (
                session.query(User)
                .filter_by(phone=phone)
                .first()
            )

            if existing:
                return False, "Phone number is already registered."

        # Create user
        user = User(
            name=name,
            email=email if email else None,
            phone=phone if phone else None,
        )

        user.set_password(password)

        session.add(user)
        session.commit()
        
        session.refresh(user)

        verification_token = create_token(
            user.id,
            VERIFY_EMAIL
        )

        send_verification_email(
            user,
            verification_token
        )

        return True, (
            "Registration successful. "
            "Please check your email to verify your account."
        )
    except Exception as e:

            session.rollback()

            import traceback
            traceback.print_exc()

            return False, f"Registration Error: {e}"

# =====================================================
# Login User
# =====================================================

def login_user(username, password):

    session = SessionLocal()

    try:

        username = (username or "").strip().lower()

        
        
        if not username:
            return False, "Email or phone is required.", None

        if not password:
            return False, "Password is required.", None

        # Login using Email
        if "@" in username:

            user = (
                session.query(User)
                .filter_by(email=username)
                .first()
            )

        # Login using Phone
        else:

            user = (
                session.query(User)
                .filter_by(phone=username)
                .first()
            )

        if not user:
            return False, "Account not found.", None
        
        if user.email and not user.email_verified:
            return (
                False,
                "Please verify your email before logging in.",
                None
            )

        if not user.check_password(password):
            return False, "Invalid password.", None

        return True, "Login successful.", user

    except Exception as e:

        print("Login Error:", e)

        return False, "Something went wrong during login.", None

    finally:

        session.close()
        

def forgot_password(email):

    session = SessionLocal()

    try:

        email = (email or "").strip().lower()

        if not email:
            return False, "Email is required."

        user = (
            session.query(User)
            .filter_by(email=email)
            .first()
        )

        # Don't reveal whether the email exists
        if not user:
            return (
                True,
                "If an account with that email exists, a password reset link has been sent."
            )

        token = create_token(
            user.id,
            RESET_PASSWORD
        )

        send_password_reset_email(
            user,
            token
        )

        return (
            True,
            "If an account with that email exists, a password reset link has been sent."
        )

    finally:

        session.close()
        
def reset_password(token, new_password):

    session = SessionLocal()

    try:

        print("Token:", token)

        user_token = verify_token(
            token,
            RESET_PASSWORD
        )

        print("User Token:", user_token)

        if not user_token:
            return False, "Invalid or expired reset link."

        user = session.get(
            User,
            user_token.user_id
        )

        print("User:", user)

        if not user:
            return False, "User not found."

        user.set_password(new_password)

        print("New Hash:", user.password_hash)

        session.commit()

        delete_token(token)

        return True, "Password updated successfully."

    except Exception as e:

        session.rollback()

        print(e)

        return False, str(e)

    finally:

        session.close()
        
        

def resend_verification_email(email):

    session = SessionLocal()

    try:

        email = (email or "").strip().lower()

        if not email:
            return False, "Email is required."

        user = (
            session.query(User)
            .filter_by(email=email)
            .first()
        )

        if not user:
            return False, "No account found with that email."

        if user.email_verified:
            return False, "Email is already verified."

        token = create_token(
            user.id,
            VERIFY_EMAIL
        )

        send_verification_email(
            user,
            token
        )

        return True, "Verification email sent successfully."

    finally:

        session.close()