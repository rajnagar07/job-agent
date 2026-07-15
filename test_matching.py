from database.db import SessionLocal
from database.models import Job

from services.matching_service import match_resume_with_job

session = SessionLocal()

jobs = session.query(Job).all()

for job in jobs:
    print(job.title)
    
result = match_resume_with_job(
    "uploads/a9076e5a-e4f7-400a-985c-a32e815a1ab4.pdf",
    job
)

print(result)

session.close()