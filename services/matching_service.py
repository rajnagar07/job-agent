from services.resume_service import extract_resume_text

from ai.matcher import (
    match_resume_with_ai,
    calculate_match_score
)

from ai.skill_extractor import extract_skills
from ai.job_skill_extractor import extract_job_skills

from database.db import SessionLocal
from database.models import Job

import traceback


# ============================================================
# SINGLE JOB - AI MATCH
# ============================================================

def match_resume_with_job(
    resume_path,
    job
):

    # Extract resume
    resume_text = extract_resume_text(
        resume_path
    )

    return ai_match_resume_with_job(
        resume_text,
        job
    )


# ============================================================
# SINGLE JOB - FAST RULE MATCH
# ============================================================

def fast_match_resume_with_job(
    resume_skills,
    job
):

    print("=" * 60)
    print("JOB:", job.title)

    job_skills = extract_job_skills(
        job
    )

    print(
        "Resume Skills:",
        resume_skills
    )

    print(
        "Job Skills:",
        job_skills
    )

    result = calculate_match_score(
        resume_skills,
        job_skills
    )

    print(
        "Result:",
        result
    )

    result["method"] = "Rule Based"

    return result


# ============================================================
# SINGLE JOB - AI MATCH FROM ALREADY EXTRACTED RESUME
# ============================================================

def ai_match_resume_with_job(resume_text, job):
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text is empty.")

    if not job:
        raise ValueError("Job information is missing.")

    job_text = f"""
Job Title: {job.title or "Not specified"}
Company: {job.company or "Not specified"}
Location: {job.location or "Not specified"}
Experience: {job.experience or "Not specified"}
Salary: {job.salary or "Not specified"}

Description:
{job.description or "No description provided."}
"""

    try:
        result = match_resume_with_ai(
            resume_text,
            job_text
        )

        if not isinstance(result, dict):
            raise ValueError("AI returned an invalid response.")

        result["method"] = "AI"
        return result

    except Exception:
        logger.exception(
            "AI matching failed for job ID %s",
            getattr(job, "id", "unknown")
        )
        raise



# ============================================================
# MATCH RESUME AGAINST ALL ACTIVE JOBS
# ============================================================


def match_resume_with_all_jobs(resume_path):
    session = SessionLocal()

    try:
        # Step 1: Extract resume once
        resume_text = extract_resume_text(resume_path)

        # Step 2: Extract resume skills once
        resume_skills = extract_skills(resume_text)

        print("\nRESUME SKILLS:", resume_skills)

        # Step 3: Fetch active jobs
        jobs = (
            session.query(Job)
            .filter(Job.status == "active")
            .all()
        )

        print(f"Active Jobs: {len(jobs)}")

        # Step 4: Rule-based matching
        recommendations = []

        for job in jobs:
            try:
                result = fast_match_resume_with_job(
                    resume_skills,
                    job
                )

                resume_score = int(result.get("score", 0))
                filter_score = int(job.filter_score or 0)

                final_score = round(
                    resume_score * 0.8 + filter_score * 0.2
                )

                recommendations.append({
                    "job": job,
                    "score": final_score,
                    "resume_score": resume_score,
                    "filter_score": filter_score,
                    "matched": result.get("matched", []),
                    "missing": result.get("missing", []),
                    "method": "Rule Based",
                    "ai_score": None,
                    "rule_score": final_score,
                })

            except Exception as e:
                print(f"Failed matching job {job.id}: {e}")

        # Step 5: Sort and filter candidates
        recommendations.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        print("TOTAL JOBS COMPARED:", len(recommendations))

        candidates = [
            item for item in recommendations
            if item["score"] >= 40
        ][:5]

        print(f"Candidates sent to Gemini: {len(candidates)}")

        if not candidates:
            return []

        # Step 6: AI reranking with a safe fallback
        try:
            ai_results = ai_rerank_recommendations(
                resume_text,
                candidates
            )

            if ai_results:
                results = ai_results
            else:
                results = candidates

        except Exception as e:
            print(f"AI reranking failed; using rule-based results: {e}")
            results = candidates

        # Step 7: Ensure fallback results have consistent fields
        for item in results:
            item.setdefault("ai_score", None)
            item.setdefault("rule_score", item.get("score", 0))
            item.setdefault("method", "Rule Based")

        print("FINAL RECOMMENDATIONS:", len(results))

        for item in results[:3]:
            print(
                f"{item['job'].title} | "
                f"Final: {item.get('score')} | "
                f"AI: {item.get('ai_score')} | "
                f"Rule: {item.get('rule_score')} | "
                f"Method: {item.get('method')}"
            )

        return results

    finally:
        session.close()

# ============================================================
# LEGACY FUNCTION
# ============================================================

def match_resume_with_all_jobs_and_save(resume_path):

    session = SessionLocal()

    try:

        resume_text = extract_resume_text(
            resume_path
        )

        resume_skills = extract_skills(
            resume_text
        )

        jobs = (
            session.query(Job)
            .filter(
                Job.status == "active"
            )
            .all()
        )

        results = []

        for job in jobs:

            try:

                result = fast_match_resume_with_job(
                    resume_skills,
                    job
                )

                resume_score = int(
                    result.get(
                        "score",
                        0
                    )
                )

                filter_score = int(
                    job.filter_score or 0
                )

                final_score = round(
                    (resume_score * 0.8) +
                    (filter_score * 0.2)
                )

                results.append({

                    "job": job,

                    "score": final_score,

                    "resume_score": resume_score,

                    "filter_score": filter_score,

                    "matched": result.get(
                        "matched",
                        []
                    ),

                    "missing": result.get(
                        "missing",
                        []
                    ),

                    "method": "Rule Based",

                })

            except Exception as e:

                print(
                    f"Failed matching job "
                    f"{job.id}: {e}"
                )

                continue

        # Remove weak recommendations
        results = [
            item
            for item in results
            if item["score"] >= 40
        ]

        # Highest score first
        results.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return results[:5]

    except Exception:

        session.rollback()

        traceback.print_exc()

        raise

    finally:

        session.close()
        


import logging

logger = logging.getLogger(__name__)


def ai_rerank_recommendations(resume_text, recommendations):

    ai_recommendations = []
    top_candidates = recommendations[:1]

    for item in top_candidates:
        job = item["job"]
        rule_score = int(item.get("score", 0))

        try:
            result = ai_match_resume_with_job(
                resume_text,
                job
            )

            ai_score = max(
                0,
                min(100, int(result.get("score", 0)))
            )

            final_score = round(
                (rule_score * 0.4) +
                (ai_score * 0.6)
            )

            ai_recommendations.append({
                "job": job,
                "score": final_score,
                "ai_score": ai_score,
                "rule_score": rule_score,
                "resume_score": item.get("resume_score", 0),
                "filter_score": item.get("filter_score", 0),
                "matched": result.get("matched", []),
                "missing": result.get("missing", []),
                "strengths": result.get("strengths", []),
                "recommendations": result.get("recommendations", []),
                "resume_summary": result.get("resume_summary", ""),
                "job_summary": result.get("job_summary", ""),
                "verdict": result.get("verdict", ""),
                "method": "AI",
            })

        except Exception:
            logger.exception(
                "AI matching failed for job ID %s",
                getattr(job, "id", "unknown")
            )

            # Preserve the rule-based recommendation.
            ai_recommendations.append({
                "job": job,
                "score": rule_score,
                "ai_score": None,
                "rule_score": rule_score,
                "resume_score": item.get("resume_score", 0),
                "filter_score": item.get("filter_score", 0),
                "matched": item.get("matched", []),
                "missing": item.get("missing", []),
                "strengths": [],
                "recommendations": [],
                "resume_summary": "",
                "job_summary": "",
                "verdict": "Rule Based Only",
                "method": "Rule Based",
            })

    ai_recommendations.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return ai_recommendations[:5]
