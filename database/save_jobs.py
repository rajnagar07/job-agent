from database.db import SessionLocal
from database.models import Job


def save_jobs(jobs):
    session = SessionLocal()

    for job in jobs:

        exists = session.query(Job).filter(Job.url == job["url"]).first()

        if exists:
            continue
        # new_job = Job(
        #     company=job.get("company"),
        #     title=job.get("position"),
        #     location=job.get("location"),
        #     salary=str(job.get("salary")),
        #     url=job.get("url"),
        #     description=job.get("description", ""),
        #     source=job.get("source", "RemoteOK"),
        #     status="New",
        #     match_score=0
        # )
        new_job = Job(
        company=job["company"],
        title=job["position"],
        description=job.get("description", ""),
        location=job["location"],
        salary=str(job["salary"]),
        url=job["url"]
    )
        session.add(new_job)

    session.commit()
    session.close()