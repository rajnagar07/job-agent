from services.resume_service import extract_resume_text
from ai.matcher import match_resume_with_ai, calculate_match_score
from ai.skill_extractor import extract_skills
from ai.job_skill_extractor import extract_job_skills
from database.db import SessionLocal
from database.models import Job
# from services.matching_service import match_resume_with_job
import traceback



def match_resume_with_job(resume_path, job):

    resume_text = extract_resume_text(resume_path)

    job_text = f"""
    Job Title: {job.title}

    Company: {job.company}

    Location: {job.location}

    Experience: {job.experience}

    Salary: {job.salary}

    Description:
    {job.description or ""}
    """

    try:

        print("\n===== USING GEMINI AI =====")

        result = match_resume_with_ai(
            resume_text,
            job_text
        )

        result["method"] = "AI"

        return result

    except Exception as e:

        print("\n========== AI ERROR ==========")
        traceback.print_exc()
        print("==============================\n")
        print("Falling back to Rule Based Matching...")

        resume_skills = extract_skills(resume_text)
        job_skills = extract_job_skills(job)

        result = calculate_match_score(
            resume_skills,
            job_skills
        )

        result.update({
            "strengths": [],
            "recommendations": [],
            "resume_summary": "",
            "job_summary": "",
            "verdict": "Rule Based Analysis",
            "method": "Rule Based"
        })

        return result
    
def match_resume_with_all_jobs(resume_path):
    session = SessionLocal()

    jobs = session.query(Job).all()

    for job in jobs:
        result = match_resume_with_job(resume_path, job)

        job.match_score = result["score"]

    session.commit()
    session.close()
    
def fast_match_resume_with_job(
    resume_skills,
    job
):

    job_skills = extract_job_skills(job)

    result = calculate_match_score(
        resume_skills,
        job_skills
    )

    result["method"] = "Rule Based"

    return result

def ai_match_resume_with_job(
    resume_text,
    job
):

    job_text = f"""
Job Title: {job.title}

Company: {job.company}

Location: {job.location}

Experience: {job.experience}

Salary: {job.salary}

Description:
{job.description or ""}
"""

    result = match_resume_with_ai(
        resume_text,
        job_text
    )

    result["method"] = "AI"

    return result