from dotenv import load_dotenv
import os

# =====================================
# Load Environment Variables
# =====================================
load_dotenv()

# =====================================
# API Keys
# =====================================
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# =====================================
# Email Configuration
# =====================================
EMAIL = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# =====================================
# Flask Configuration
# =====================================
FLASK_SECRET_KEY = os.getenv(
    "FLASK_SECRET_KEY",
    "raj_ai_job_agent_secret"
)

# =====================================
# Job Sources
# =====================================
REMOTE_OK_URL = "https://remoteok.com/api"

# =====================================
# Upload Configuration
# =====================================
UPLOAD_FOLDER = "uploads"

# =====================================
# Job Filtering Keywords
# =====================================
KEYWORDS = [
    "python",
    "backend",
    "software engineer",
    "software developer",
    "backend developer",
    "full stack",
    "fullstack",
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
    "flask",
    "fastapi",
    "django",
    "sql",
    "postgresql",
    "mysql",
    "mongodb",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "git",
    "rest api",
    "microservices",
]