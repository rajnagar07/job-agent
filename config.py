import os
from dotenv import load_dotenv


# ============================================================
# Load Environment Variables
# ============================================================

load_dotenv()


# ============================================================
# AI Configuration
# ============================================================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise RuntimeError(
        "GOOGLE_API_KEY is not configured in the .env file"
    )


# ============================================================
# Flask Configuration
# ============================================================

FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

if not FLASK_SECRET_KEY:
    raise RuntimeError(
        "FLASK_SECRET_KEY is not configured in the .env file"
    )


# ============================================================
# Application Configuration
# ============================================================

APP_URL = os.getenv(
    "APP_URL",
    "http://127.0.0.1:5000"
)


# ============================================================
# Email / Resend Configuration
# ============================================================

RESEND_API_KEY = os.getenv("RESEND_API_KEY")

FROM_EMAIL = os.getenv(
    "FROM_EMAIL",
    "AI Job Agent <onboarding@resend.dev>"
)


# ============================================================
# Legacy Email Configuration
# Keep only if some existing code still uses SMTP.
# ============================================================

EMAIL = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


# ============================================================
# Twilio Configuration
# ============================================================

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
PHONE = os.getenv("PHONE")


# ============================================================
# Database Configuration
# ============================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///jobs.db"
)


# ============================================================
# Job Sources
# ============================================================

REMOTE_OK_URL = "https://remoteok.com/api"


# ============================================================
# Upload Configuration
# ============================================================

UPLOAD_FOLDER = "uploads"


# ============================================================
# Job Filtering Keywords
# ============================================================

KEYWORDS = [
    # Programming
    "python",

    # Software Engineering
    "backend",
    "software engineer",
    "software developer",
    "backend developer",
    "full stack",
    "fullstack",

    # AI / ML
    "ai engineer",
    "machine learning",
    "deep learning",
    "data scientist",
    "data engineer",
    "genai",
    "llm",
    "rag",
    "nlp",
    "computer vision",

    # Python Frameworks
    "flask",
    "fastapi",
    "django",

    # Databases
    "sql",
    "postgresql",
    "mysql",
    "mongodb",

    # DevOps / Cloud
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",

    # Development Tools
    "git",
    "rest api",
    "microservices",
]


# ============================================================
# Greenhouse Companies
# ============================================================

GREENHOUSE_COMPANIES = [
    "stripe",
    "openai",
    "notion",
    "datadog",
    "coinbase",
    "canva",
    "rippling",
    "figma",
]


# ============================================================
# Hybrid Job Filter Thresholds
# ============================================================

JOB_FILTER_ACCEPT_THRESHOLD = 80

JOB_FILTER_REJECT_THRESHOLD = 20


# ============================================================
# Recommendation Configuration
# ============================================================

TOP_RECOMMENDATIONS = 5