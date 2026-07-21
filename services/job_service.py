from jobs.remoteok import get_jobs as remote_jobs
from jobs.wellfound import get_jobs as wellfound_jobs
from jobs.greenhouse import get_jobs as greenhouse_jobs
from config import GREENHOUSE_COMPANIES


TECH_KEYWORDS = [
    "software engineer",
    "backend",
    "frontend",
    "full stack",
    "python",
    "django",
    "flask",
    "fastapi",
    "react",
    "machine learning",
    "ml engineer",
    "ai engineer",
    "data engineer",
    "security engineer",
    "devops",
    "site reliability",
    "platform engineer",
    "android engineer",
    "ios engineer",
]

def filter_jobs(jobs):
    filtered = []

    for job in jobs:
        title = (job.get("title") or "").lower()

        if any(keyword in title for keyword in TECH_KEYWORDS):
            filtered.append(job)

    return filtered


def collect_jobs():
    jobs = []

    # Collect jobs from RemoteOK
    jobs.extend(remote_jobs())

    # Collect jobs from Wellfound
    jobs.extend(wellfound_jobs())

    # Collect jobs from Greenhouse
    for company in GREENHOUSE_COMPANIES:
        try:
            print(f"Collecting Greenhouse jobs from {company}...")
            jobs.extend(greenhouse_jobs(company))
        except Exception as e:
            print(f"Failed to fetch {company}: {e}")
    jobs = filter_jobs(jobs)
    return jobs