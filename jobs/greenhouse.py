import requests
import re
from html import unescape
from concurrent.futures import ThreadPoolExecutor, as_completed


BASE_URL = "https://boards-api.greenhouse.io/v1/boards"


GREENHOUSE_BOARDS = [
    "stripe",
    "datadog",
    "coinbase",
    "figma",
]


# ============================================================
# Clean HTML
# ============================================================

def clean_html(html):

    if not html:
        return ""

    text = re.sub(r"<[^>]+>", " ", html)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# Get Job Details
# ============================================================

def get_job_details(board, job_id):

    url = f"{BASE_URL}/{board}/jobs/{job_id}"

    response = requests.get(
        url,
        timeout=15
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# Normalize Job
# ============================================================

def normalize_job(job, details):

    description = clean_html(
        details.get("content", "")
    )

    return {
        "title": job.get("title"),
        "company": job.get("company_name"),

        "location": (
            job.get("location", {}).get("name")
            if job.get("location")
            else ""
        ),

        "description": description,

        "salary": None,
        "experience": None,

        "posted_date": job.get(
            "first_published"
        ),

        "url": job.get(
            "absolute_url"
        ),

        "source": "Greenhouse",
    }


# ============================================================
# Fetch One Complete Job
# ============================================================

def fetch_complete_job(board, job):

    try:

        job_id = job.get("id")

        if not job_id:
            return None

        details = get_job_details(
            board,
            job_id
        )

        return normalize_job(
            job,
            details
        )

    except Exception as e:

        print(
            f"Failed job {job.get('id')}: {e}"
        )

        return None


# ============================================================
# Get Jobs From One Board
# ============================================================

def get_jobs(board):

    url = f"{BASE_URL}/{board}/jobs"

    response = requests.get(
        url,
        timeout=15
    )

    response.raise_for_status()

    jobs = response.json().get(
        "jobs",
        []
    )

    print(
        f"{board}: {len(jobs)} jobs found"
    )

    complete_jobs = []

    # --------------------------------------------------------
    # Fetch job details concurrently
    # --------------------------------------------------------

    with ThreadPoolExecutor(
        max_workers=3
    ) as executor:

        futures = [
            executor.submit(
                fetch_complete_job,
                board,
                job
            )
            for job in jobs
        ]

        for future in as_completed(futures):

            result = future.result()

            if result:
                complete_jobs.append(result)

    return complete_jobs


# ============================================================
# Get Jobs From All Boards
# ============================================================

def get_all_jobs():

    all_jobs = []

    for board in GREENHOUSE_BOARDS:

        print(
            f"\nCollecting Greenhouse jobs from {board}..."
        )

        try:

            jobs = get_jobs(board)

            all_jobs.extend(jobs)

            print(
                f"{board}: {len(jobs)} jobs collected"
            )

        except Exception as e:

            print(
                f"Failed to fetch {board}: {e}"
            )

    return all_jobs


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":

    jobs = get_all_jobs()

    print(
        f"\nTotal Jobs: {len(jobs)}"
    )

    if jobs:

        first_job = jobs[0]

        print("\nFirst Job:")
        print(first_job)

        print(
            "\nDescription length:",
            len(
                first_job.get(
                    "description",
                    ""
                )
            )
        )