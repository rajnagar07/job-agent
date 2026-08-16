import time
import traceback
from datetime import datetime

from database.db import SessionLocal
from database.models import Task

from services.job_service import run_job_collection


def process_tasks():

    session = SessionLocal()

    try:

        task = (
            session.query(Task)
            .filter(
                Task.status == "pending"
            )
            .order_by(
                Task.created_at.asc()
            )
            .first()
        )

        if not task:
            return False

        print(
            f"Starting task {task.id}: "
            f"{task.task_type}"
        )

        task.status = "running"
        task.started_at = datetime.utcnow()

        session.commit()

        try:

            if task.task_type == "job_scraper":

                run_job_collection()

            task.status = "completed"
            task.completed_at = datetime.utcnow()

            session.commit()

            print(
                f"Task {task.id} completed successfully."
            )

        except Exception as e:

            session.rollback()

            task.status = "failed"
            task.error = str(e)
            task.completed_at = datetime.utcnow()

            session.commit()

            print(
                f"Task {task.id} failed: {e}"
            )

            traceback.print_exc()

        return True

    finally:

        session.close()


if __name__ == "__main__":

    print("Background worker started.")

    while True:

        try:

            processed = process_tasks()

            if not processed:

                time.sleep(5)

        except Exception as e:

            print(
                f"Worker error: {e}"
            )

            traceback.print_exc()

            time.sleep(5)