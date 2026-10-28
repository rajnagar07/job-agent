
import logging

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableLambda
from config import GOOGLE_API_KEY

logger = logging.getLogger(__name__)

primary_model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.3,
    timeout=20,
    max_retries=1,
)

fallback_model = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.3,
    timeout=20,
    max_retries=1,
)


def invoke_with_fallback(messages):
    try:
        return primary_model.invoke(messages)
    except Exception:
        logger.exception("Primary Gemini model failed; trying fallback.")
        return fallback_model.invoke(messages)


chat_model = RunnableLambda(invoke_with_fallback)
