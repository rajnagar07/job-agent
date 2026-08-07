from database.db import SessionLocal
from database.models import Job
from ai.skill_extractor import extract_skills


def fast_rank_jobs(resume_text):

    session = SessionLocal()

    try:

        resume_skills = set(
            skill.lower()
            for skill in extract_skills(resume_text)
        )

        jobs = (
            session.query(Job)
            .filter(Job.status == "active")
            .all()
        )

        ranked_jobs = []

        for job in jobs:

            job_skills = set(
                skill.lower()
                for skill in extract_skills(job.description or "")
            )

            matched = resume_skills & job_skills

            missing = job_skills - resume_skills

            score = 0

            if job_skills:
                score = round(
                    len(matched) / len(job_skills) * 100
                )

            ranked_jobs.append({

                "job": job,

                "score": score,

                "matched_skills": list(matched),

                "missing_skills": list(missing)

            })

        ranked_jobs.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return ranked_jobs[:5]

    finally:

        session.close()