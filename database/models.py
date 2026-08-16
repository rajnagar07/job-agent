from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey
)

from sqlalchemy.orm import relationship

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database.db import Base


# ============================================================
# Background Tasks
# ============================================================

class Task(Base):
    __tablename__ = "tasks"

    id = Column(
        Integer,
        primary_key=True
    )

    task_type = Column(
        String(50),
        nullable=False
    )

    status = Column(
        String(20),
        default="pending",
        nullable=False
    )

    error = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    started_at = Column(
        DateTime,
        nullable=True
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )



# ============================================================
# User
# ============================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(120),
        unique=True,
        index=True,
        nullable=True
    )

    phone = Column(
        String(20),
        unique=True,
        index=True,
        nullable=True
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    email_verified = Column(
        Boolean,
        default=False,
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationship
    tokens = relationship(
        "UserToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )


# ============================================================
# User Tokens
# ============================================================

class UserToken(Base):
    __tablename__ = "user_tokens"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    token = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    # verify_email / reset_password
    token_type = Column(
        String(30),
        nullable=False
    )

    expires_at = Column(
        DateTime,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="tokens"
    )


# ============================================================
# Jobs
# ============================================================

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)

    company = Column(
        String,
        nullable=False
    )

    title = Column(
        String,
        nullable=False
    )
    skills = Column(
    Text,
    nullable=True
    )

    location = Column(String)

    experience = Column(String)

    salary = Column(String)

    source = Column(String)

    posted_date = Column(String)

    description = Column(Text)

    url = Column(
        String,
        unique=True,
        nullable=False
    )

    match_score = Column(
        Integer,
        default=0
    )
    filter_score = Column(
        Integer,
        default=0
    )
    # -----------------------------
    # Lifecycle
    # -----------------------------

    status = Column(
        String(20),
        default="active",
        nullable=False
    )

    last_seen = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    last_scrape_id = Column(
        Integer,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    expires_at = Column(
        DateTime,
        nullable=True
    )


# ============================================================
# Scrape Logs
# ============================================================

class ScrapeLog(Base):
    __tablename__ = "scrape_logs"

    id = Column(Integer, primary_key=True)

    started_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    finished_at = Column(
        DateTime
    )

    source = Column(String)

    jobs_found = Column(
        Integer,
        default=0
    )

    new_jobs = Column(
        Integer,
        default=0
    )

    updated_jobs = Column(
        Integer,
        default=0
    )
    expired_jobs = Column(
    Integer,
    default=0
    )

    errors = Column(
        Integer,
        default=0
    )

    error_message = Column(
        Text,
        nullable=True
    )

    status = Column(
        String(20),
        default="running"
    )
    
class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    job_id = Column(
        Integer,
        ForeignKey("jobs.id"),
        nullable=False
    )

    match_score = Column(
        Integer,
        default=0
    )

    matched_skills = Column(Text)

    missing_skills = Column(Text)

    reason = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    job = relationship("Job")
    user = relationship("User")
    