import sqlite3

DB_PATH = "jobs.db"

conn = sqlite3.connect(DB_PATH)

try:
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(jobs)")
    columns = [row[1] for row in cursor.fetchall()]

    if "filter_score" not in columns:
        cursor.execute(
            """
            ALTER TABLE jobs
            ADD COLUMN filter_score INTEGER DEFAULT 0
            """
        )

        conn.commit()

        print("Added filter_score column successfully.")

    else:
        print("filter_score already exists.")

finally:
    conn.close()