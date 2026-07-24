from datetime import datetime, timedelta

from database.db import SessionLocal
from database.models import Job


def expire_jobs(current_scrape_id, allowed_missed_scrapes=3):
    """
    Expire jobs that have not appeared in the last
    `allowed_missed_scrapes` successful scrape runs.
    """

    session = SessionLocal()

    try:
        expired_count = 0

        active_jobs = session.query(Job).filter(
            Job.status == "active"
        ).all()

        for job in active_jobs:

            if job.last_scrape_id is None:
                continue

            missed_scrapes = current_scrape_id - job.last_scrape_id

            if missed_scrapes >= allowed_missed_scrapes:
                job.status = "expired"
                job.expires_at = datetime.utcnow() + timedelta(days=30)

                expired_count += 1

        session.commit()

        print(f"Expired Jobs : {expired_count}")

        return expired_count

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()
        
                
def delete_expired_jobs():
    """
    Permanently delete jobs whose expires_at date has passed.
    """

    session = SessionLocal()

    try:

        deleted = session.query(Job).filter(
            Job.status == "expired",
            Job.expires_at <= datetime.utcnow()
        ).delete()

        session.commit()

        print(f"Deleted Jobs : {deleted}")

        return deleted

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()