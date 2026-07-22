from database.db import SessionLocal
from database.models import Job


def save_jobs(jobs):

    session = SessionLocal()

    for job in jobs:

        exists = session.query(Job).filter_by(
            url=job.get("url")
        ).first()

        if exists:
            continue

        new_job = Job(
            company=job.get("company"),
            title=job.get("title"),
            location=job.get("location"),
            experience=job.get("experience"),
            salary=str(job.get("salary", "")),
            source=job.get("source"),
            posted_date=job.get("posted_date"),
            description=job.get("description"),
            url=job.get("url"),
            match_score=0,
            status="New"
        )

        session.add(new_job)

    session.commit()
    session.close()