from database.db import SessionLocal
from database.models import Job


def get_recommendations(limit=20):
    session = SessionLocal()

    try:
        jobs = (
            session.query(Job)
            .filter(Job.status == "active")
            .order_by(Job.match_score.desc())
            .limit(limit)
            .all()
        )

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