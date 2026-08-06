from database.db import SessionLocal
from database.models import User, UserToken

session = SessionLocal()

try:
    deleted_tokens = session.query(UserToken).delete()
    deleted_users = session.query(User).delete()

    session.commit()

    print(f"Deleted {deleted_users} users")
    print(f"Deleted {deleted_tokens} tokens")

finally:
    session.close()