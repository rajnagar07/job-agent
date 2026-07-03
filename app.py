from services.job_service import collect_jobs
from jobs.utils import filter_jobs

from database.models import Base
from database.db import engine
from database.save_jobs import save_jobs

Base.metadata.create_all(bind=engine)

jobs = collect_jobs()

print("Before filter:", len(jobs))

jobs = filter_jobs(jobs)

print("After filter:", len(jobs))

for job in jobs:
    print(job["position"])

save_jobs(jobs)

print("Jobs Saved Successfully")