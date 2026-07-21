import requests

BASE_URL = "https://boards-api.greenhouse.io/v1/boards"

def normalize_job(job):
    return {
        "title": job.get("title"),
        "company": job.get("company_name"),
        "location": job.get("location", {}).get("name"),
        "description": None,          # Not available from this endpoint
        "url": job.get("absolute_url"),
        "source": "Greenhouse"
    }
def get_jobs(company):
    """
    Fetch jobs from a Greenhouse board.
    """

    url = f"{BASE_URL}/{company}/jobs"

    response = requests.get(url, timeout=15)

    response.raise_for_status()

    jobs = response.json()["jobs"]
    # print(jobs[0].keys())   # <-- print BEFORE normalization

    return [normalize_job(job) for job in jobs]