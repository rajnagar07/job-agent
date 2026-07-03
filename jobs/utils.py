import re

PATTERNS = [
    r"\bpython\b",
    r"\bbackend\b",
    r"\bsoftware engineer\b",
    r"\bsoftware developer\b",
    r"\bassociate software engineer\b",
    r"\bai engineer\b",
    r"\bgenai\b",
    r"\bllm\b",
    r"\brag\b",
    r"\bflask\b",
    r"\bfastapi\b",
    r"\bdjango\b",
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