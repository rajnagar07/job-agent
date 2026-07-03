import requests

URL = "https://remoteok.com/api"

headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_jobs():
    response = requests.get(URL, headers=headers)

    if response.status_code != 200:
        print("Failed to fetch jobs")
        return []

    data = response.json()

    jobs = []

    # Skip the metadata element
    for job in data[1:]:
        jobs.append({
            "company": job.get("company"),
            "position": job.get("position"),
            "location": job.get("location"),
            "salary": job.get("salary_min"),
            "url": job.get("url")
        })

    return jobs