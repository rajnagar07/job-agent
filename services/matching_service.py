from services.resume_service import extract_resume_text
from ai.matcher import match_resume_with_ai, calculate_match_score
from ai.skill_extractor import extract_skills
from ai.job_skill_extractor import extract_job_skills
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