import requests
import re
from html import unescape

BASE_URL = "https://boards-api.greenhouse.io/v1/boards"

# Only verified working boards
GREENHOUSE_BOARDS = [
    "stripe",
    "datadog",
    "coinbase",
    "figma",
]


def normalize_job(job):
    return {
        "title": job.get("title"),
        "company": job.get("company_name"),
        "location": job.get("location", {}).get("name"),
        "description": None,
        "salary": None,
        "experience": None,
        "posted_date": job.get("first_published"),
        "url": job.get("absolute_url"),
        "source": "Greenhouse",
    }


def clean_html(html):
    if not html:
        return ""

    text = re.sub(r"<[^>]+>", " ", html)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def get_job_details(board: str, job_id: int):
    url = f"{BASE_URL}/{board}/jobs/{job_id}"

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    return response.json()


def get_jobs(board):
    url = f"{BASE_URL}/{board}/jobs"

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    jobs = response.json()["jobs"]

    return [normalize_job(job) for job in jobs]


def get_all_jobs():
    all_jobs = []

    for board in GREENHOUSE_BOARDS:
        print(f"Collecting Greenhouse jobs from {board}...")

        try:
            jobs = get_jobs(board)
            all_jobs.extend(jobs)

        except Exception as e:
            print(f"Failed to fetch {board}: {e}")

    return all_jobs


if __name__ == "__main__":
    jobs = get_all_jobs()

    print(f"\nTotal Jobs: {len(jobs)}")

    if jobs:
        print(jobs[0])