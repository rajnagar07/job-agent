import logging
from datetime import datetime

from database.db import SessionLocal
from database.models import ScrapeLog
from database.save_jobs import save_jobs

from services.lifecycle_service import expire_old_jobs
from jobs.utils import filter_jobs

from jobs.remoteok import get_jobs as remote_jobs
from jobs.wellfound import get_jobs as wellfound_jobs
from jobs.greenhouse import get_all_jobs

logger = logging.getLogger(__name__)


# =====================================================
# Collect Jobs From All Sources
# =====================================================

def collect_jobs():

    jobs = []

    sources = [
        ("RemoteOK", remote_jobs),
        ("Wellfound", wellfound_jobs),
        ("Greenhouse", get_all_jobs),
    ]

    for source_name, scraper in sources:

        try:

            logger.info(f"Collecting jobs from {source_name}...")

            source_jobs = scraper()

            logger.info(
                f"{source_name}: {len(source_jobs)} jobs collected."
            )

            jobs.extend(source_jobs)

        except Exception as e:

            logger.exception(
                f"{source_name} scraper failed: {e}"
            )

    logger.info(f"Total Collected Jobs: {len(jobs)}")

    return jobs


# =====================================================
# Complete Scraper Pipeline
# =====================================================

def run_job_collection():

    session = SessionLocal()

    start_time = datetime.utcnow()

    scrape_log = ScrapeLog(
        started_at=start_time,
        status="running"
    )

    session.add(scrape_log)
    session.commit()

    try:

        # ----------------------------------------
        # Collect Jobs
        # ----------------------------------------

        jobs = collect_jobs()

        scrape_log.jobs_found = len(jobs)

        # ----------------------------------------
        # Filter Jobs
        # ----------------------------------------

        filtered_jobs = filter_jobs(jobs)

        logger.info(
            f"Filtered Jobs: {len(filtered_jobs)}"
        )

        # ----------------------------------------
        # Save Jobs
        # ----------------------------------------

        new_jobs, updated_jobs = save_jobs(
            filtered_jobs,
            scrape_log.id
        )

        # ----------------------------------------
        # Expire Old Jobs
        # ----------------------------------------

        expired_jobs = expire_old_jobs(
            scrape_log.id
        )

        # ----------------------------------------
        # Update Scrape Log
        # ----------------------------------------

        scrape_log.new_jobs = new_jobs
        scrape_log.updated_jobs = updated_jobs
        scrape_log.expired_jobs = expired_jobs

        scrape_log.finished_at = datetime.utcnow()
        scrape_log.status = "success"

        session.commit()

        duration = (
            scrape_log.finished_at - start_time
        ).total_seconds()

        logger.info("=" * 60)
        logger.info("Daily Scrape Summary")
        logger.info(f"Collected Jobs : {len(jobs)}")
        logger.info(f"Filtered Jobs  : {len(filtered_jobs)}")
        logger.info(f"New Jobs       : {new_jobs}")
        logger.info(f"Updated Jobs   : {updated_jobs}")
        logger.info(f"Expired Jobs   : {expired_jobs}")
        logger.info(f"Duration       : {duration:.2f} sec")
        logger.info("=" * 60)

        return filtered_jobs

    except Exception as e:

        session.rollback()

        scrape_log.finished_at = datetime.utcnow()
        scrape_log.status = "failed"
        scrape_log.errors = 1
        scrape_log.error_message = str(e)

        session.commit()

        logger.exception("Job collection failed.")

        raise

    finally:

        session.close()