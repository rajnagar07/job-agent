from flask import Flask, render_template, request, redirect, url_for, flash
from database.db import SessionLocal
from database.models import Job
from utils.text_cleaner import clean_job_description
import services.resume_service as resume_service
import os
import uuid
from werkzeug.utils import secure_filename
from ai.resume_analyzer import analyze_resume_with_ai
from services.matching_service import (
    match_resume_with_job,
    fast_match_resume_with_job,
    ai_match_resume_with_job,
)
from services.job_service import run_job_collection
from ai.skill_extractor import extract_skills
from services.recommendation_service import get_recommendations, get_dashboard_stats,get_job,get_badge
from auth.routes import auth_bp
from database.models import Base
from database.db import engine
from auth.decorators import login_required
from database.models import User
import logging
import threading


logger = logging.getLogger(__name__)
Base.metadata.create_all(bind=engine)

def extract_text_from_pdf(filepath):
    # Support multiple possible function names in services.resume_service
    candidates = [
        "extract_text_from_pdf",
        "extract_resume_text",
        "extract_text_from_resume",
        "extract_text",
        "extract_resume",
    ]
    for name in candidates:
        func = getattr(resume_service, name, None)
        if callable(func):
            return func(filepath)
    raise AttributeError("No supported PDF text extraction function found in services.resume_service")
# ===========================
# Base Directory
# ===========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ===========================
# Flask App
# ===========================
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)



app.config["SECRET_KEY"] = os.getenv(
    "FLASK_SECRET_KEY",
    "raj_ai_job_agent_secret"
)

app.register_blueprint(auth_bp)

# ===========================
# Flask Login
# ===========================



# app.secret_key = os.getenv(
#     "FLASK_SECRET_KEY",
#     "raj_ai_job_agent_secret"
# )

# ===========================
# Upload Configuration
# ===========================
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# entry point
@app.route("/")
def landing():
    return render_template("landing.html")


# ===========================
# Dashboard
# ===========================
@app.route("/jobs")
def index():

    session = SessionLocal()

    try:

        search = request.args.get("search", "")

        query = session.query(Job)

        if search:
            query = query.filter(Job.title.ilike(f"%{search}%"))

        jobs = query.all()

        total_jobs = len(jobs)
        companies = len(set(job.company for job in jobs))
        sources = len(set(job.source for job in jobs))

        return render_template(
            "index.html",
            jobs=jobs,
            total_jobs=total_jobs,
            companies=companies,
            sources=sources,
            search=search,
        )

    finally:
        session.close()


# ===========================
# Job Details
# ===========================
@app.route("/job/<int:job_id>")
@login_required
def job_details(job_id):

    session = SessionLocal()

    try:

        job = session.query(Job).filter(Job.id == job_id).first()

        if not job:
            return "Job Not Found", 404

        # Clean the description before displaying
        cleaned_description = clean_job_description(job.description)

        return render_template(
            "job_details.html",
            job=job,
            cleaned_description=cleaned_description,
        )
    finally:
            session.close()


# ===========================
# Upload Resume
# ===========================
@app.route("/upload_resume/<int:job_id>", methods=["GET", "POST"])
@login_required
def upload_resume(job_id):

    session = SessionLocal()

    try:

        job = session.query(Job).filter(Job.id == job_id).first()

        if not job:
            return "Job Not Found", 404

        cleaned_description = clean_job_description(job.description)

        if request.method == "POST":

            file = request.files.get("resume")

            if not file or not file.filename:
                flash("Please select a PDF file.", "warning")
                return redirect(url_for("upload_resume", job_id=job_id))

            if not file.filename.lower().endswith(".pdf"):
                flash("Only PDF files are allowed.", "danger")
                return redirect(url_for("upload_resume", job_id=job_id))

            filename = f"{uuid.uuid4()}.pdf"
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            file.save(filepath)

            try:

                result = match_resume_with_job(
                    filepath,
                    job
                )

                job.match_score = result["score"]

                session.commit()

                return render_template(
                    "match_result.html",
                    job=job,
                    result=result
                )

            finally:

                if os.path.exists(filepath):
                    os.remove(filepath)

        return render_template(
            "upload_resume.html",
            job=job,
            cleaned_description=cleaned_description
        )

    except Exception as e:

        session.rollback()

        flash(
            f"Resume analysis failed: {str(e)}",
            "danger"
        )

        return redirect(
            url_for(
                "upload_resume",
                job_id=job_id
            )
        )

    finally:
        session.close()

@app.route("/resume-analysis", methods=["GET", "POST"])
@login_required
def resume_analysis():

    if request.method == "POST":

        # -----------------------------
        # Validate Upload
        # -----------------------------
        if "resume" not in request.files:
            flash("Please upload a resume.", "danger")
            return redirect(request.url)

        file = request.files["resume"]
        filename = file.filename or ""

        if filename == "":
            flash("Please select a PDF file.", "warning")
            return redirect(request.url)

        if not filename.lower().endswith(".pdf"):
            flash("Only PDF files are allowed.", "danger")
            return redirect(request.url)

        try:

            # -----------------------------
            # Save PDF
            # -----------------------------
            filename = f"{uuid.uuid4()}.pdf"

            filepath = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )

            file.save(filepath)

            # -----------------------------
            # Extract Resume Text
            # -----------------------------
            resume_text = extract_text_from_pdf(filepath)
            resume_text = str(resume_text)

            if not resume_text.strip():

                flash("Unable to read the uploaded resume.", "danger")
                return redirect(request.url)

            # -----------------------------
            # AI Resume Analysis
            # -----------------------------

            # Replace this with your Gemini function

            analysis = analyze_resume_with_ai(resume_text)

            # Example:
            #
            # analysis = analyze_resume_with_ai(resume_text)

            return render_template(
                "resume_result.html",
                analysis=analysis
            )

        except Exception as e:

            print(e)

            flash("Something went wrong while analyzing the resume.", "danger")

            return redirect(request.url)

    return render_template("resume_analysis.html")

# ===========================
# Recommend Jobs
# ===========================
@app.route("/recommend-jobs", methods=["GET", "POST"])
@login_required
def recommend_jobs():

    session = SessionLocal()
    filepath = None

    try:

        # ====================================================
        # SHOW UPLOAD PAGE
        # ====================================================

        if request.method == "GET":
            return render_template(
                "recommend_jobs.html"
            )

        # ====================================================
        # VALIDATE RESUME
        # ====================================================

        if "resume" not in request.files:

            flash(
                "Please upload your resume.",
                "danger"
            )

            return redirect(
                request.url
            )

        file = request.files["resume"]

        filename = file.filename or ""

        if filename == "":

            flash(
                "Please select your resume.",
                "warning"
            )

            return redirect(
                request.url
            )

        if not filename.lower().endswith(".pdf"):

            flash(
                "Only PDF files are allowed.",
                "danger"
            )

            return redirect(
                request.url
            )

        # ====================================================
        # SAVE RESUME
        # ====================================================

        filename = f"{uuid.uuid4()}.pdf"

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(filepath)

        # ====================================================
        # EXTRACT RESUME
        # ====================================================

        resume_text = extract_text_from_pdf(
            filepath
        )

        resume_text = str(
            resume_text
        )

        if not resume_text.strip():

            flash(
                "Unable to read the uploaded resume.",
                "danger"
            )

            return redirect(
                request.url
            )

        # ====================================================
        # EXTRACT RESUME SKILLS ONCE
        # ====================================================

        resume_skills = extract_skills(
            resume_text
        )

        print("\n========================================")
        print("RESUME SKILLS")
        print("========================================")
        print(resume_skills)

        # ====================================================
        # LOAD ALL ACTIVE JOBS
        # ====================================================

        jobs = (
            session.query(Job)
            .filter(
                Job.status == "active"
            )
            .all()
        )

        print(
            f"\nACTIVE JOBS: {len(jobs)}"
        )

        # ====================================================
        # FAST MATCH ALL ACTIVE JOBS
        # ====================================================

        recommendations = []

        for job in jobs:

            # Skip completely empty jobs
            if (
                job.title is None
                and job.description is None
            ):
                continue

            try:

                result = (
                    fast_match_resume_with_job(
                        resume_skills,
                        job
                    )
                )

                recommendations.append({

                    "job": job,

                    "result": result

                })

            except Exception as e:

                print(
                    f"Failed matching job "
                    f"{job.id}: {e}"
                )

                continue

        # ====================================================
        # TOTAL JOBS COMPARED
        # ====================================================

        total_matches = len(
            recommendations
        )

        print(
            "\n========================================"
        )

        print(
            "TOTAL JOBS COMPARED:",
            total_matches
        )

        # ====================================================
        # SORT ALL JOBS
        # ====================================================

        recommendations.sort(
            key=lambda x: int(
                x["result"].get(
                    "score",
                    0
                )
            ),
            reverse=True
        )

        # ====================================================
        # CALCULATE STATS BEFORE GEMINI
        # ====================================================

        best_match = (
            int(
                recommendations[0]["result"].get(
                    "score",
                    0
                )
            )
            if recommendations
            else 0
        )

        average_match = (
            round(
                sum(
                    int(
                        item["result"].get(
                            "score",
                            0
                        )
                    )
                    for item in recommendations
                )
                / len(recommendations),
                1
            )
            if recommendations
            else 0
        )

        # ====================================================
        # TOP 5 ONLY
        # ====================================================

        top_recommendations = (
            recommendations[:5]
        )

        print(
            "\n========================================"
        )

        print(
            "TOP 5 MATCHES"
        )

        print(
            "========================================"
        )

        for index, item in enumerate(
            top_recommendations,
            start=1
        ):

            print(
                f"{index}. "
                f"{item['job'].title} "
                f"→ "
                f"{item['result'].get('score', 0)}%"
            )

        # ====================================================
        # GEMINI ANALYSIS — TOP 5 ONLY
        # ====================================================

        for item in top_recommendations:

            try:

                ai_result = (
                    ai_match_resume_with_job(
                        resume_text,
                        item["job"]
                    )
                )

                item["result"] = ai_result

            except Exception as e:

                print(
                    f"Gemini failed for "
                    f"{item['job'].title}: {e}"
                )

                # Keep rule-based result
                # if Gemini fails

        # ====================================================
        # RENDER TOP 5
        # ====================================================

        return render_template(
            "recommended_jobs.html",

            recommendations=(
                top_recommendations
            ),

            total_matches=(
                total_matches
            ),

            best_match=(
                best_match
            ),

            average_match=(
                average_match
            )
        )

    except Exception as e:

        import traceback

        traceback.print_exc()

        flash(
            f"Recommendation failed: {str(e)}",
            "danger"
        )

        return redirect(
            request.url
        )

    finally:

        session.close()

        if (
            filepath
            and os.path.exists(filepath)
        ):

            os.remove(filepath)



@app.route("/recommendations")
@login_required
def recommendations():

    min_score = request.args.get("min_score", type=int)
    company = request.args.get("company")
    location = request.args.get("location")
    source = request.args.get("source")

    jobs = get_recommendations(
        min_score=min_score,
        company=company,
        location=location,
        source=source
    )

    stats = get_dashboard_stats()

    return render_template(
        "recommendations.html",
        jobs=jobs,
        stats=stats
    )
    
@app.route("/recommendation/<int:job_id>")
@login_required
def recommendation_details(job_id):

    job = get_job(job_id)

    return render_template(
        "recommendation_details.html",
        job=job
    )
    
# ===========================
# Run Job Scraper
# ===========================


@app.route("/run-scraper")
@login_required
def run_scraper_route():

    def scraper_task():

        try:
            logger.info("=" * 60)
            logger.info("BACKGROUND SCRAPER STARTED")
            logger.info("=" * 60)

            jobs = run_job_collection()

            logger.info(
                "BACKGROUND SCRAPER FINISHED: %s JOBS",
                len(jobs)
            )

        except Exception:
            logger.exception("BACKGROUND SCRAPER FAILED")

    thread = threading.Thread(
        target=scraper_task,
        daemon=True
    )

    thread.start()

    return """
        <h2>Job scraper started successfully.</h2>
        <p>The scraper is running in the background.</p>
        <p>Wait a few minutes and then open the Jobs page.</p>
# ===========================
# Run Application
# ===========================
if __name__ == "__main__":
    app.run()