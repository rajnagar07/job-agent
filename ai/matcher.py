import json
import time
from ai.chatmodel import chat_model
from ai.prompts import match_prompt


def calculate_match_score(resume_skills, job_skills):

    resume = set(skill.lower() for skill in resume_skills)
    job = set(skill.lower() for skill in job_skills)

    matched = resume.intersection(job)
    missing = job - resume

    if not job:
        score = 0
    else:
        score = int((len(matched) / len(job)) * 100)

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

            print("\n===== GEMINI RESPONSE =====")
            print(content)
            print("===========================\n")

            if content.startswith("```"):
                content = content.replace("```json", "").replace("```", "").strip()

            return json.loads(content)

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(5)

    raise Exception("Gemini API unavailable after multiple retries.")