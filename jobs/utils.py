import re
from config import KEYWORDS

PATTERNS = [
    rf"\b{re.escape(keyword)}\b"
    for keyword in KEYWORDS
]

def filter_jobs(jobs):
    filtered = []

    for job in jobs:
        title = (job.get("position") or "").lower()
        description = (job.get("description") or "").lower()

        text = f"{title} {description}"

        if any(re.search(pattern, text) for pattern in PATTERNS):
            filtered.append(job)

    return filtered