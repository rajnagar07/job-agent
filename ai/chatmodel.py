from langchain_google_genai import ChatGoogleGenerativeAI   # type: ignore

from config import GOOGLE_API_KEY

chat_model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    google_api_key=GOOGLE_API_KEY,
    temperature=0,
)