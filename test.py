from services.job_service import collect_jobs
jobs = collect_jobs()

print(len(jobs))

for job in jobs:
    print(job["title"])