from flask import Flask, render_template,request
from database.db import SessionLocal
from database.models import Job
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
@app.route("/")
def index():
    session = SessionLocal()

    search = request.args.get("search", "")

    if search:
        jobs = session.query(Job).filter(
            Job.title.ilike(f"%{search}%")
        ).all()
    else:
        jobs = session.query(Job).all()

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
        search=search
)


@app.route("/job/<int:job_id>")
def job_details(job_id):

    session = SessionLocal()

    job = session.query(Job).filter(Job.id == job_id).first()

    session.close()

    if not job:
        return "Job Not Found", 404

    return render_template(
        "job_details.html",
        job=job
    )


if __name__ == "__main__":
    app.run(debug=True)