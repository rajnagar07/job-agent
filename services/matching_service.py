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
        # Fast match ALL jobs
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

                score = int(
                    result.get(
                        "score",
                        0
                    )
                )

                recommendations.append({

                    "job": job,

                    "score": score,

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
        # Show Top 5
        # ====================================================

        top_5 = recommendations[:5]

        print(
            "TOP 5 MATCHES"
        )

        print(
            "========================================"
        )

        for index, item in enumerate(
            top_5,
            start=1
        ):

            print(
                f"{index}. "
                f"{item['job'].title} "
                f"→ {item['score']}%"
            )

        # ====================================================
        # STEP 7
        # Return Top 5
        # ====================================================

        return top_5

    finally:

        session.close()


# ============================================================
# LEGACY FUNCTION
# ============================================================

def match_resume_with_all_jobs_and_save(
    resume_path
):

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

            result = fast_match_resume_with_job(
                resume_skills,
                job
            )

            job.match_score = int(
                result.get(
                    "score",
                    0
                )
            )

            results.append({
                "job": job,
                "score": result.get(
                    "score",
                    0
                ),
                "matched": result.get(
                    "matched",
                    []
                ),
                "missing": result.get(
                    "missing",
                    []
                )
            })

        session.commit()

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