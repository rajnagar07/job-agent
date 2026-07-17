from jobs.remoteok import get_jobs

jobs = get_jobs()

print(f"\nTotal jobs fetched: {len(jobs)}")