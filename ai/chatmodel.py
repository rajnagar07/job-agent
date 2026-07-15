from langchain_google_genai import ChatGoogleGenerativeAI   # type: ignore

from config import GEMINI_API_KEY

chat_model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0,
)