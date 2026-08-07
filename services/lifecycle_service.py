from datetime import datetime

from database.db import SessionLocal
from database.models import Job


def expire_old_jobs(scrape_id):

    session = SessionLocal()

    try:

        expired_jobs = session.query(Job).filter(
            Job.last_scrape_id != scrape_id,
            Job.status == "active"
        ).all()

        for job in expired_jobs:

            job.status = "expired"
            job.expires_at = datetime.utcnow()

        session.commit()

        return len(expired_jobs)

    finally:

        session.close()