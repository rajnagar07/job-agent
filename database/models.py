from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime
)

from database.db import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)

    company = Column(String, nullable=False)
    title = Column(String, nullable=False)
    location = Column(String)

    experience = Column(String)
    salary = Column(String)

    source = Column(String)
    posted_date = Column(String)

    description = Column(Text)

    url = Column(String, unique=True, nullable=False)

    match_score = Column(Integer, default=0)

    # ----------------------------
    # Job Lifecycle Management
    # ----------------------------

    # active | expired
    status = Column(String(20), default="active", nullable=False)

    # Last time this job was found during scraping
    last_seen = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    last_scrape_id = Column(Integer, nullable=True)
    # When job was first added
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Updated whenever any job field changes
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Scheduled deletion date after expiry
    expires_at = Column(DateTime, nullable=True)
    
    
class ScrapeLog(Base):
    __tablename__ = "scrape_logs"

    id = Column(Integer, primary_key=True)

    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime)

    source = Column(String)

    jobs_found = Column(Integer, default=0)
    new_jobs = Column(Integer, default=0)
    updated_jobs = Column(Integer, default=0)

    status = Column(String(20), default="running")