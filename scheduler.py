from apscheduler.schedulers.blocking import BlockingScheduler

from app import run_scraper

scheduler = BlockingScheduler()

# Every day at 9 AM
scheduler.add_job(
    run_scraper,
    trigger="cron",
    hour=9,
    minute=0
)

print("Scheduler Started")
print("Scraper will run every day at 09:00")

run_scraper()

scheduler.start()