from database.db import SessionLocal
from database.models import Job
from services.badge_service import get_badge


def get_recommendations(limit=20,
    min_score=None,
    company=None,
    location=None,
    source=None):
    session = SessionLocal()

    try:
        query = session.query(Job).filter(Job.status == "active")

        if min_score:
            query = query.filter(Job.match_score >= min_score)

        if company:
            query = query.filter(Job.company == company)

        if location:
            query = query.filter(Job.location == location)

        if source:
            query = query.filter(Job.source == source)

        jobs = (
            query
            .order_by(Job.match_score.desc())
            .limit(limit)
            .all()
        )

        # Add AI badge to each job
        for job in jobs:
            job.badge = get_badge(job.match_score)

        return jobs

    finally:
        session.close()


def get_dashboard_stats():
    session = SessionLocal()

    try:
        jobs = (
            session.query(Job)
            .filter(Job.status == "active")
            .order_by(Job.match_score.desc())
            .limit(20)
            .all()
        )

        total = len(jobs)

        top_match = jobs[0].match_score if jobs else 0

        avg_match = (
            round(sum(job.match_score for job in jobs) / total, 1)
            if total else 0
        )

        return {
            "top_match": top_match,
            "total": total,
            "average": avg_match,
            "resume_status": "Uploaded"
        }

    finally:
        session.close()
        
def get_job(job_id):
    session = SessionLocal()

    try:
        job = (
            session.query(Job)
            .filter(Job.id == job_id)
            .first()
        )

        if job:
            job.badge = get_badge(job.match_score)

        return job

    finally:
        session.close()