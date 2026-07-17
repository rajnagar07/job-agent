from database.db import SessionLocal
from database.models import Job
from ai.skill_extractor import extract_skills

session = SessionLocal()

job = session.query(Job).order_by(Job.id.desc()).first()
if job is None:
    print("No jobs found")
    session.close()
    raise SystemExit(0)

text = f"{job.title}\n{job.description or ''}"

# print("JOB DESCRIPTION:")
# print(text)

# print("\nSKILLS:")
# print(extract_skills(text))

print("TITLE:")
print(job.title)

print("\nDESCRIPTION:")
print(repr(job.description))

session.close()