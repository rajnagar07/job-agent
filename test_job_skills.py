from database.db import SessionLocal
from database.models import Job
from ai.skill_extractor import extract_skills

session = SessionLocal()

job = session.query(Job).first()

text = f"{job.title}\n{job.description or ''}"

print("TEXT:")
print(text)

print("\nSKILLS:")
print(extract_skills(text))

session.close()