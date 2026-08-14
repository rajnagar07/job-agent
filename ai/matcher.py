import json
import time
from ai.chatmodel import chat_model
from ai.prompts import match_prompt



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

    # No job skills
    if not job:
        return {
            "score": 0,
            "matched": [],
            "missing": [],
        }

    matched = resume.intersection(job)
    missing = job - resume

    # Skill coverage
    skill_score = (
        len(matched) / len(job)
    ) * 100

    score = round(skill_score)

    return {
        "score": score,
        "matched": sorted(matched),
        "missing": sorted(missing),
    }


def match_resume_with_ai(resume_text, job_description):

    chain = match_prompt | chat_model

    for attempt in range(3):

        try:

            response = chain.invoke({
                "resume": resume_text,
                "job": job_description
            })

            content = response.content

            if isinstance(content, list):
                content = "".join(
                    item.get("text", "")
                    for item in content
                    if item.get("type") == "text"
                )

            content = content.strip()

            if content.startswith("```"):
                content = (
                    content.replace("```json", "")
                    .replace("```", "")
                    .strip()
                )

            print("\n===== GEMINI RESPONSE =====")
            print(content)
            print("===========================\n")

            result = json.loads(content)

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

            print(f"Attempt {attempt + 1} failed: {e}")

            if attempt < 2:
                time.sleep(5)

    raise Exception("Gemini API unavailable after multiple retries.")

