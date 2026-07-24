from datetime import datetime

from database.db import SessionLocal
from database.models import Job


def delete_expired_jobs():
    """
    Permanently delete jobs whose expiration date has passed.
    """

    session = SessionLocal()

    try:
        jobs_to_delete = session.query(Job).filter(
            Job.status == "expired",
            Job.expires_at != None,
            Job.expires_at <= datetime.utcnow()
        ).all()

        deleted_count = len(jobs_to_delete)

        for job in jobs_to_delete:
            session.delete(job)

        session.commit()

        print(f"Deleted Jobs : {deleted_count}")

        return deleted_count

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()