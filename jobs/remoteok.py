import requests
from config import REMOTE_OK_URL

URL = REMOTE_OK_URL

headers = {
    "User-Agent": "Mozilla/5.0"
}


def normalize_job(job):
    return {
        "title": job.get("position"),
        "company": job.get("company"),
        "location": job.get("location"),
        "description": job.get("description"),
        "salary": job.get("salary_min"),
        "url": job.get("url"),
        "source": "RemoteOK"
    }


def get_jobs():

    response = requests.get(URL, headers=headers)

    if response.status_code != 200:
        print("Failed to fetch jobs")
        return []

    data = response.json()

    jobs = []

    # Skip metadata
    for job in data[1:]:
        jobs.append(normalize_job(job))

    return jobs