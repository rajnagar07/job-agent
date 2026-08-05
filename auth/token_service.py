import secrets
from datetime import datetime, timedelta

from database.db import SessionLocal
from database.models import UserToken


# ==========================================================
# Token Types
# ==========================================================

VERIFY_EMAIL = "verify_email"
RESET_PASSWORD = "reset_password"


# ==========================================================
# Create Token
# ==========================================================

def create_token(user_id, token_type, expires_in_hours=24):

    session = SessionLocal()

    try:

        # Remove old token of same type
        session.query(UserToken).filter(
            UserToken.user_id == user_id,
            UserToken.token_type == token_type
        ).delete()

        token = secrets.token_urlsafe(32)

        user_token = UserToken(
            user_id=user_id,
            token=token,
            token_type=token_type,
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours)
        )

        session.add(user_token)
        session.commit()

        return token

    except Exception as e:

        session.rollback()
        print("Token Creation Error:", e)
        return None

    finally:

        session.close()


# ==========================================================
# Verify Token
# ==========================================================

def verify_token(token, token_type):

    session = SessionLocal()

    try:

        user_token = (
            session.query(UserToken)
            .filter_by(
                token=token,
                token_type=token_type
            )
            .first()
        )

        if not user_token:
            return None

        if user_token.expires_at < datetime.utcnow():

            session.delete(user_token)
            session.commit()

            return None

        return user_token

    finally:

        session.close()


# ==========================================================
# Delete Token
# ==========================================================

def delete_token(token):

    session = SessionLocal()

    try:

        user_token = (
            session.query(UserToken)
            .filter_by(token=token)
            .first()
        )

        if user_token:
            session.delete(user_token)
            session.commit()

    finally:

        session.close()


# ==========================================================
# Delete Expired Tokens
# ==========================================================

def cleanup_expired_tokens():

    session = SessionLocal()

    try:

        deleted = (
            session.query(UserToken)
            .filter(
                UserToken.expires_at < datetime.utcnow()
            )
            .delete()
        )

        session.commit()

        print(f"Deleted {deleted} expired tokens.")

    finally:

        session.close()