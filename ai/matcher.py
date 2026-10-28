import json
import time
import logging

from ai.chatmodel import chat_model
from ai.prompts import match_prompt

logger = logging.getLogger(__name__)


def match_resume_with_ai(resume_text, job_description):
    chain = match_prompt | chat_model

    for attempt in range(2):
        try:
            response = chain.invoke({
                "resume": resume_text,
                "job": job_description
            })

            content = response.content

            if isinstance(content, list):
                content = "".join(
                    block.get("text", "")
                    for block in content
                    if isinstance(block, dict)
                    and block.get("type") == "text"
                )

            if not isinstance(content, str):
                raise ValueError("Gemini returned invalid content.")

            content = content.strip()

            if content.startswith("```"):
                content = (
                    content.replace("```json", "")
                    .replace("```", "")
                    .strip()
                )

            result = json.loads(content)

            if not isinstance(result, dict):
                raise ValueError("Gemini response must be a JSON object.")

            required_keys = {
                "score",
                "matched",
                "missing",
                "strengths",
                "recommendations",
                "resume_summary",
                "job_summary",
                "verdict",
            }

            missing_keys = required_keys - result.keys()

            if missing_keys:
                raise ValueError(
                    f"Gemini response missing keys: {missing_keys}"
                )

            return result

        except Exception as e:
            logger.warning(
                "Gemini attempt %s/2 failed: %s",
                attempt + 1,
                e
            )

            if attempt == 0:
                time.sleep(2)

    raise RuntimeError(
        "Gemini matching failed after two attempts."
    )


def calculate_match_score(resume_skills, job_skills):
    # Normalize skills
    resume = {
        skill.strip().lower()
        for skill in resume_skills
        if skill and skill.strip()
    }

    job = {
        skill.strip().lower()
        for skill in job_skills
        if skill and skill.strip()
    }

    if not job:
        return {
            "score": 0,
            "matched": [],
            "missing": [],
        }

    matched = resume.intersection(job)
    missing = job - resume

    score = round((len(matched) / len(job)) * 100)

    return {
        "score": score,
        "matched": sorted(matched),
        "missing": sorted(missing),
    }
