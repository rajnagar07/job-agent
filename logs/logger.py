import logging

logging.basicConfig(
    filename="logs/job_agent.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


logging.basicConfig(
    filename="logs/scheduler.log",
    level=logging.INFO,
    format="%(asctime)s %(message)s"
)

logger = logging.getLogger(__name__)