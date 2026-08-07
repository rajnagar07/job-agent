from apscheduler.schedulers.blocking import BlockingScheduler

from app import run_scraper

scheduler = BlockingScheduler()

# ==========================================
# Daily Job Scraper
# Runs every day at 09:00 AM
# ==========================================

scheduler.add_job(
    func=run_scraper,
    trigger="cron",
    hour=9,
    minute=0,
    id="daily_scraper",
    replace_existing=True,
)

print("=" * 60)
print("AI Job Agent Scheduler Started")
print("Daily Job Scraper Scheduled")
print("Time : Every Day at 09:00 AM")
print("=" * 60)

if __name__ == "__main__":

    # Uncomment only if you want to run immediately
    # run_scraper()

    scheduler.start()