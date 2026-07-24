import re

# Roles we want to keep
KEYWORDS = [
    # Software Engineering
    "software engineer",
    "software developer",
    "backend",
    "backend engineer",
    "backend developer",
    "frontend",
    "frontend engineer",
    "frontend developer",
    "full stack",
    "fullstack",
    "full-stack",

    # Python
    "python",
    "django",
    "flask",
    "fastapi",

    # AI / ML
    "machine learning",
    "ml engineer",
    "ai engineer",
    "artificial intelligence",
    "llm",
    "rag",
    "nlp",
    "genai",
    "generative ai",
    "langchain",

    # Data
    "data engineer",

    # General
    "developer",
    "engineer",
]


# Roles to ignore
EXCLUDE_KEYWORDS = [
    "ios",
    "android",
    "react native",
    "flutter",
    "sales",
    "marketing",
    "account executive",
    "customer success",
    "hr",
    "human resources",
    "finance",
    "legal",
    "designer",
    "graphic designer",
    "product designer",
    "ui designer",
    "ux designer",
    "recruiter",
    "intern recruiter",
]


def clean_text(text):
    if not text:
        return ""

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Lowercase
    text = text.lower()

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def filter_jobs(jobs):
    filtered = []

    for job in jobs:

        title = clean_text(job.get("title", ""))
        description = clean_text(job.get("description", ""))

        text = f"{title} {description}"

        # Reject unwanted roles
        if any(word in text for word in EXCLUDE_KEYWORDS):
            continue

        # Keep relevant roles
        if any(word in text for word in KEYWORDS):
            filtered.append(job)

    return filtered