from flask import Flask, render_template, request, redirect, url_for, flash
from database.db import SessionLocal
from database.models import Job
from utils.text_cleaner import clean_job_description
import services.resume_service as resume_service
import os
import uuid
from werkzeug.utils import secure_filename
from ai.resume_analyzer import analyze_resume_with_ai
from services.matching_service import (match_resume_with_job,fast_match_resume_with_job)
from ai.skill_extractor import extract_skills

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

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "raj_ai_job_agent_secret"
)

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
def resume_analysis():

    if request.method == "POST":

        # -----------------------------
        # Validate Upload
        # -----------------------------
        if "resume" not in request.files:
            flash("Please upload a resume.", "danger")
            return redirect(request.url)

        file = request.files["resume"]

        if file.filename == "":
            flash("Please select a PDF file.", "warning")
            return redirect(request.url)

        if not file.filename.lower().endswith(".pdf"):
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
def recommend_jobs():

    session = SessionLocal()
    filepath = None      # <-- Add this line


    try:

        # Show upload page
        if request.method == "GET":
            return render_template("recommend_jobs.html")

        # ----------------------------------
        # Validate Upload
        # ----------------------------------
        if "resume" not in request.files:

            flash("Please upload a resume.", "danger")

            return redirect(request.url)

        file = request.files["resume"]

        if file.filename == "":

            flash("Please select a PDF file.", "warning")

            return redirect(request.url)

        if not file.filename.lower().endswith(".pdf"):

            flash("Only PDF files are allowed.", "danger")

            return redirect(request.url)

        # ----------------------------------
        # Save Resume
        # ----------------------------------
        filename = f"{uuid.uuid4()}.pdf"

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(filepath)
        
        resume_text = extract_text_from_pdf(filepath)

        resume_skills = extract_skills(
            resume_text
        )

        # ----------------------------------
        # Get All Jobs
        # ----------------------------------
        jobs = session.query(Job).all()

        recommendations = []
        for job in jobs:
            result = fast_match_resume_with_job(
                resume_skills,
                job
            )

            job.match_score = result["score"]

            recommendations.append({
                "job": job,
                "result": result
            })

        session.commit()
        # ----------------------------------
        # Sort by Match Score
        # ----------------------------------
        recommendations.sort(
            key=lambda x: x["result"]["score"],
            reverse=True
        )

        # ----------------------------------
        # Keep Only Top 20
        # ----------------------------------
        recommendations = recommendations[:20]

        # ----------------------------------
        # Gemini Analysis (Top 20 Only)
        # ----------------------------------

        for item in recommendations:

            ai_result = match_resume_with_job(
                filepath,
                item["job"]
            )

            item["result"] = ai_result

            item["job"].match_score = ai_result["score"]

        session.commit()

        return render_template(
            "recommended_jobs.html",
            recommendations=recommendations,
            total_matches=len(recommendations),
            best_match=recommendations[0]["result"]["score"] if recommendations else 0
)
    except Exception as e:

        session.rollback()

        flash(
            f"Recommendation failed: {str(e)}",
            "danger"
        )

        return redirect(request.url)

    finally:
        session.close()

        if filepath and os.path.exists(filepath):
            os.remove(filepath)
# ===========================
# Run Application
# ===========================
if __name__ == "__main__":
    app.run(debug=True)