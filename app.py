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


#### this one for just testing 
# from jobs.remoteok import get_jobs as remote_jobs
# from jobs.wellfound import get_jobs as wellfound_jobs

# remote = remote_jobs()
# wellfound = wellfound_jobs()

# print("RemoteOK:", len(remote))
# print("Wellfound:", len(wellfound))

# jobs = remote + wellfound


# print("Total:", len(jobs))

