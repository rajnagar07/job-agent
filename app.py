from database.models import Base
from database.db import engine

from services.job_service import collect_jobs
from jobs.utils import filter_jobs

from database.save_jobs import save_jobs

from services.scrape_log import start_scrape, finish_scrape
from services.job_lifecycle import expire_jobs
from services.job_cleanup import delete_expired_jobs

Base.metadata.create_all(bind=engine)


def run_scraper():

    print("=" * 60)
    print("Running Daily Job Scraper")
    print("=" * 60)

    scrape_id = start_scrape(
        "RemoteOK + Wellfound + Greenhouse"
    )

    jobs = collect_jobs()

    print(f"Collected Jobs : {len(jobs)}")

    jobs = filter_jobs(jobs)

    print(f"Filtered Jobs : {len(jobs)}")

    new_jobs, updated_jobs = save_jobs(
        jobs,
        scrape_id
    )

    expire_jobs(scrape_id)

    delete_expired_jobs()

    finish_scrape(
        scrape_id=scrape_id,
        jobs_found=len(jobs),
        new_jobs=new_jobs,
        updated_jobs=updated_jobs
    )

    print("Daily Scrape Completed")


if __name__ == "__main__":
    run_scraper()