from datetime import datetime

from database.db import SessionLocal
from database.models import Job


def save_jobs(jobs, scrape_id):
    session = SessionLocal()

    new_jobs = 0
    updated_jobs = 0

    try:
        for job in jobs:

            existing_job = session.query(Job).filter_by(
                url=job.get("url")
            ).first()

            if existing_job:
                # ----------------------------
                # Update Existing Job
                # ----------------------------
                existing_job.company = job.get("company")
                existing_job.title = job.get("title")
                existing_job.location = job.get("location")
                existing_job.experience = job.get("experience")
                existing_job.salary = str(job.get("salary", ""))
                existing_job.source = job.get("source")
                existing_job.posted_date = job.get("posted_date")
                existing_job.description = job.get("description")

                # Job Lifecycle
                existing_job.status = "active"
                existing_job.last_seen = datetime.utcnow()
                existing_job.last_scrape_id = scrape_id
                existing_job.updated_at = datetime.utcnow()
                existing_job.expires_at = None

                updated_jobs += 1

            else:
                # ----------------------------
                # Insert New Job
                # ----------------------------
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

                    # Lifecycle Fields
                    status="active",
                    last_seen=datetime.utcnow(),
                    last_scrape_id=scrape_id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    expires_at=None
                )

                session.add(new_job)
                new_jobs += 1

        session.commit()

        print("\n========== Save Summary ==========")
        print(f"New Jobs     : {new_jobs}")
        print(f"Updated Jobs : {updated_jobs}")
        print("==================================\n")

        return new_jobs, updated_jobs

    except Exception as e:
        session.rollback()
        print(f"Error while saving jobs: {e}")
        raise

    finally:
        session.close()