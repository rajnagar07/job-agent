
import json
import time
import logging

from ai.chatmodel import chat_model
from ai.prompts import resume_analysis_prompt

logger = logging.getLogger(__name__)


def analyze_resume_with_ai(resume_text):
    start_time = time.perf_counter()

    try:
        chain = resume_analysis_prompt | chat_model

        logger.info("Resume analysis: starting Gemini request")

        response = chain.invoke({
            "resume": resume_text
        })

        logger.info(
            "Resume analysis: Gemini responded in %.2f seconds",
            time.perf_counter() - start_time
        )

        if isinstance(response.content, list):
            content = "".join(
                block.get("text", "")
                for block in response.content
                if isinstance(block, dict)
                and block.get("type") == "text"
            )
        else:
            content = response.content

        content = content.strip()

        if content.startswith("```"):
            content = (
                content.replace("```json", "")
                .replace("```", "")
                .strip()
            )

        result = json.loads(content)

        logger.info(
            "Resume analysis completed in %.2f seconds",
            time.perf_counter() - start_time
        )

        return result

    except Exception:
        logger.exception(
            "Resume analysis failed after %.2f seconds",
            time.perf_counter() - start_time
        )

        return {
            "ats_score": 0,
            "resume_score": 0,
            "verdict": "Analysis Failed",
            "summary": "Unable to analyze resume.",
            "skills": [],
            "strengths": [],
            "weaknesses": [
                "Resume analysis failed. Please try again."
            ],
            "recommendations": [],
            "recommended_roles": []
        }
