from database.db import SessionLocal
from database.models import ScrapeLog
from datetime import datetime


def start_scrape(source="All Sources"):
    session = SessionLocal()

    scrape = ScrapeLog(
        source=source,
        status="running"
    )

    session.add(scrape)
    session.commit()
    session.refresh(scrape)

    scrape_id = scrape.id

    session.close()

    return scrape_id


def finish_scrape(scrape_id, jobs_found, new_jobs, updated_jobs):
    session = SessionLocal()

    scrape = session.get(ScrapeLog, scrape_id)

    scrape.finished_at = datetime.utcnow()
    scrape.jobs_found = jobs_found
    scrape.new_jobs = new_jobs
    scrape.updated_jobs = updated_jobs
    scrape.status = "completed"

    session.commit()
    session.close()