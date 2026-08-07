from datetime import datetime

from database.db import SessionLocal
from database.models import ScrapeLog
from database.save_jobs import save_jobs
from services.lifecycle_service import expire_old_jobs

from jobs.remoteok import get_jobs as remote_jobs
from jobs.wellfound import get_jobs as wellfound_jobs
from jobs.greenhouse import get_all_jobs


def collect_jobs():
    jobs = []

    print("Collecting jobs from RemoteOK...")
    jobs.extend(remote_jobs())

    print("Collecting jobs from Wellfound...")
    jobs.extend(wellfound_jobs())

    print("Collecting jobs from Greenhouse...")
    jobs.extend(get_all_jobs())

    return jobs


def run_job_collection():

    session = SessionLocal()

    scrape_log = ScrapeLog(
        started_at=datetime.utcnow(),
        status="running"
    )

    session.add(scrape_log)
    session.commit()

    try:

        jobs = run_job_collection()
        scrape_log.jobs_found = len(jobs)

        new_jobs, updated_jobs = save_jobs(
            jobs,
            scrape_log.id
        )

        expired_jobs = expire_old_jobs(
            scrape_log.id
        )

        scrape_log.new_jobs = new_jobs
        scrape_log.updated_jobs = updated_jobs
        scrape_log.expired_jobs = expired_jobs

        scrape_log.finished_at = datetime.utcnow()
        scrape_log.status = "success"

        session.commit()
        
        
        #for testing 
        print("\n========== Scrape Summary ==========")
        print(f"Jobs Found   : {scrape_log.jobs_found}")
        print(f"New Jobs     : {new_jobs}")
        print(f"Updated Jobs : {updated_jobs}")
        print(f"Expired Jobs : {expired_jobs}")
        print("====================================\n")

        return jobs

    except Exception as e:

        session.rollback()

        scrape_log.finished_at = datetime.utcnow()
        scrape_log.status = "failed"
        scrape_log.errors = 1
        scrape_log.error_message = str(e)

        session.commit()

        raise

    finally:

        session.close()