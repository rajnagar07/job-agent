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

def ai_match_resume_with_job(
    resume_text,
    job
):

    job_text = f"""
Job Title: {job.title}

Company: {job.company}

Location: {job.location}

Experience: {job.experience}

Salary: {job.salary}

Description:
{job.description or ""}
"""

    result = match_resume_with_ai(
        resume_text,
        job_text
    )

    result["method"] = "AI"

    return result


# ============================================================
# MATCH RESUME AGAINST ALL ACTIVE JOBS
# ============================================================

def match_resume_with_all_jobs(
    resume_path
):

    session = SessionLocal()

    try:

        # ====================================================
        # STEP 1
        # Extract resume ONCE
        # ====================================================

        resume_text = extract_resume_text(
            resume_path
        )

        # ====================================================
        # STEP 2
        # Extract resume skills ONCE
        # ====================================================

        resume_skills = extract_skills(
            resume_text
        )

        print("\n========================================")
        print("RESUME SKILLS")
        print("========================================")
        print(resume_skills)

        # ====================================================
        # STEP 3
        # Get ACTIVE jobs only
        # ====================================================

        jobs = (
            session.query(Job)
            .filter(
                Job.status == "active"
            )
            .all()
        )

        print(
            f"\nActive Jobs: {len(jobs)}"
        )

        # ====================================================
        # STEP 4
        # Fast match ALL jobs (rule score + filter score blend)
        # ====================================================

        recommendations = []

        for job in jobs:

            try:

                result = (
                    fast_match_resume_with_job(
                        resume_skills,
                        job
                    )
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

                recommendations.append({

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

        # ====================================================
        # STEP 5
        # Sort ALL jobs
        # ====================================================

        recommendations.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        print(
            "\n========================================"
        )

        print(
            "TOTAL JOBS COMPARED:",
            len(recommendations)
        )

        # ====================================================
        # STEP 6
        # Filter weak matches, take Top 20
        # ====================================================
        recommendations = [
                item
                for item in recommendations
                if item["score"] >= 40
        ]
        top_20 = recommendations[:20]

        print(
            "TOP 20 CANDIDATES → SENDING TO GEMINI"
        )

        print(
            "========================================"
        )

        for index, item in enumerate(
            top_20,
            start=1
        ):

            print(
                f"{index}. "
                f"{item['job'].title} "
                f"→ {item['score']}%"
            )

        # ====================================================
        # STEP 7
        # AI re-rank Top 20 with Gemini, return Top 20
        # ====================================================

        ai_results = ai_rerank_recommendations(
            resume_text,
            top_20
        )
        print("\n========================================")
        print("FINAL AI RESULTS")
        print("========================================")

        for item in ai_results[:3]:

            print(
                "JOB:",
                item["job"].title
            )

            print(
                "FINAL SCORE:",
                item.get("score")
            )

            print(
                "AI SCORE:",
                item.get("ai_score")
            )

            print(
                "RULE SCORE:",
                item.get("rule_score")
            )

            print(
                "METHOD:",
                item.get("method")
            )

            print("----------------------------------------")
            return ai_results

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
        
def ai_rerank_recommendations(
    resume_text,
    recommendations
):

    ai_recommendations = []

    # Only send Top 20 to Gemini
    top_candidates = recommendations[:10]

    for item in top_candidates:

        job = item["job"]

        try:

            # =========================================
            # GEMINI ANALYSIS
            # =========================================

            result = ai_match_resume_with_job(
                resume_text,
                job
            )

            # =========================================
            # AI SCORE
            # =========================================

            ai_score = int(
                result.get(
                    "score",
                    0
                )
            )

            # =========================================
            # RULE-BASED SCORE
            # =========================================

            rule_score = int(
                item.get(
                    "score",
                    0
                )
            )

            # =========================================
            # FINAL SCORE
            # =========================================

            final_score = round(
                (rule_score * 0.4) +
                (ai_score * 0.6)
            )

            # =========================================
            # SAVE AI RESULT
            # =========================================

            ai_recommendations.append({

                "job": job,

                "score": final_score,

                "ai_score": ai_score,

                "rule_score": rule_score,

                "resume_score": item.get(
                    "resume_score",
                    0
                ),

                "filter_score": item.get(
                    "filter_score",
                    0
                ),

                "matched": result.get(
                    "matched",
                    []
                ),

                "missing": result.get(
                    "missing",
                    []
                ),

                "strengths": result.get(
                    "strengths",
                    []
                ),

                "recommendations": result.get(
                    "recommendations",
                    []
                ),

                "resume_summary": result.get(
                    "resume_summary",
                    ""
                ),

                "job_summary": result.get(
                    "job_summary",
                    ""
                ),

                "verdict": result.get(
                    "verdict",
                    ""
                ),

                "method": "AI",

            })

        except Exception as e:

            print(
                f"AI matching failed for "
                f"job {job.id}: {e}"
            )

            # =========================================
            # GEMINI FAILED
            # Keep Rule-Based Result
            # =========================================

            rule_score = int(
                item.get(
                    "score",
                    0
                )
            )

            ai_recommendations.append({

                "job": job,

                "score": rule_score,

                "ai_score": None,

                "rule_score": rule_score,

                "resume_score": item.get(
                    "resume_score",
                    0
                ),

                "filter_score": item.get(
                    "filter_score",
                    0
                ),

                "matched": item.get(
                    "matched",
                    []
                ),

                "missing": item.get(
                    "missing",
                    []
                ),

                "strengths": [],

                "recommendations": [],

                "resume_summary": "",

                "job_summary": "",

                "verdict": "Rule Based Only",

                "method": "Rule Based",

            })

    # =========================================
    # SORT BY FINAL SCORE
    # =========================================

    ai_recommendations.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    # =========================================
    # RETURN TOP 20
    # =========================================

    return ai_recommendations[:10]