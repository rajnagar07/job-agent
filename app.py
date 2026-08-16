import logging

from database.db import engine
from database.models import Base
from services.job_service import run_job_collection


# =====================================================
# Logging Configuration
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# =====================================================
# Create Database Tables
# =====================================================

Base.metadata.create_all(bind=engine)

# =====================================================
# Entry Point
# =====================================================

def run_scraper():

    logger.info("=" * 60)
    logger.info("AI Job Agent - Daily Job Scraper")
    logger.info("=" * 60)

    jobs = run_job_collection()

    logger.info("=" * 60)
    logger.info("Scraping Completed Successfully")
    logger.info("Total Jobs Saved : %s", len(jobs))
    logger.info("=" * 60)

    return jobs


if __name__ == "__main__":
    run_scraper()