from services.resume_service import extract_resume_text
from ai.skill_extractor import extract_skills
from ai.job_skill_extractor import extract_job_skills
from ai.matcher import calculate_match_score


def match_resume_with_job(resume_path, job):

    # Resume text
    resume_text = extract_resume_text(resume_path)

    # Resume skills
    resume_skills = extract_skills(resume_text)

    # Job skills
    job_skills = extract_job_skills(job)

    print("\nResume Skills:")
    print(resume_skills)

    print("\nJob Skills:")
    print(job_skills)

    result = calculate_match_score(
        resume_skills,
        job_skills
    )

    return result