from dotenv import load_dotenv
import os

load_dotenv()

# Environment Variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMAIL = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Job Sources
REMOTE_OK_URL = "https://remoteok.com/api"

# Job Filtering
KEYWORDS = [
    "python",
    "backend",
    "software engineer",
    "software developer",
    "backend developer",
    "ai engineer",
    "machine learning",
    "genai",
    "llm",
    "rag",
    "flask",
    "fastapi",
    "django",
]