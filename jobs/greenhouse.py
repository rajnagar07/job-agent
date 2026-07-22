import requests

import re
from html import unescape

BASE_URL = "https://boards-api.greenhouse.io/v1/boards"



def normalize_job(job, company):
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


def get_job_details(company: str, job_id: int) -> dict:
    """
    Fetch complete details of a Greenhouse job.
    """
    url = f"{BASE_URL}/{company}/jobs/{job_id}"

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    return response.json()



def get_jobs(company):
    url = f"{BASE_URL}/{company}/jobs"

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    jobs = response.json()["jobs"]

    return [normalize_job(job, company) for job in jobs]
if __name__ == "__main__":

    jobs = get_jobs("stripe")

    print(f"Total Jobs: {len(jobs)}")
    print("-" * 50)

    first = jobs[0]

    print(first)