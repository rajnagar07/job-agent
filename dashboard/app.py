from flask import Flask, render_template, request, redirect, url_for, flash
from services.matching_service import match_resume_with_job
from database.db import SessionLocal
from database.models import Job
import os
import uuid

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

app.secret_key = "raj_ai_job_agent_secret"
# ===========================
# Upload Configuration
# ===========================
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ===========================
# Dashboard
# ===========================
@app.route("/")
def index():

    session = SessionLocal()

    search = request.args.get("search", "")

    query = session.query(Job)

    if search:
        query = query.filter(Job.title.ilike(f"%{search}%"))

    jobs = query.all()

    total_jobs = len(jobs)
    companies = len(set(job.company for job in jobs))
    sources = len(set(job.source for job in jobs))

    session.close()

    return render_template(
        "index.html",
        jobs=jobs,
        total_jobs=total_jobs,
        companies=companies,
        sources=sources,
        search=search,
    )


# ===========================
# Job Details
# ===========================
@app.route("/job/<int:job_id>")
def job_details(job_id):

    session = SessionLocal()

    job = session.query(Job).filter(Job.id == job_id).first()

    session.close()

    if not job:
        return "Job Not Found", 404

    return render_template(
        "job_details.html",
        job=job,
    )


# ===========================
# Upload Resume
# ===========================
# @app.route("/upload_resume", methods=["GET", "POST"])
@app.route("/upload_resume/<int:job_id>", methods=["GET", "POST"])
def upload_resume(job_id):

    session = SessionLocal()

    job = session.query(Job).filter(Job.id == job_id).first()

    if not job:
        session.close()
        return "Job Not Found", 404

    if request.method == "POST":

        file = request.files.get("resume")

        if file and file.filename and file.filename.lower().endswith(".pdf"):

            filename = f"{uuid.uuid4()}.pdf"

            filepath = os.path.join(
                UPLOAD_FOLDER,
                filename
            )

            file.save(filepath)

            result = match_resume_with_job(filepath, job)

            session.close()

            return render_template(
                "match_result.html",
                job=job,
                result=result
            )

        flash("Please upload a valid PDF file.", "danger")

        session.close()

        return redirect(url_for("upload_resume", job_id=job_id))

    session.close()

    return render_template(
        "upload_resume.html",
        job=job
    )
# ===========================
# Run Application
# ===========================
if __name__ == "__main__":
    app.run(debug=True)

# print("Secret Key:", app.secret_key)