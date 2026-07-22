from database.db import SessionLocal
from database.models import Job

from ai.skill_extractor import extract_skills
from ai.job_skill_extractor import extract_job_skills
from ai.matcher import calculate_match_score

resume = """
Python
FastAPI
Flask
Git
SQL
LangChain
Machine Learning
"""

resume_skills = extract_skills(resume)

session = SessionLocal()

job = session.query(Job).first()

print("Job:", job.title)

job_skills = extract_job_skills(job)

print("Resume Skills :", resume_skills)
print("Job Skills    :", job_skills)

result = calculate_match_score(
    resume_skills,
    job_skills
)

print(result)

session.close()