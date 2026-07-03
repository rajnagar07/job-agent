from sqlalchemy import Column, Integer, String
from database.db import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)

    company = Column(String)
    title = Column(String)
    location = Column(String)

    experience = Column(String)
    salary = Column(String)

    source = Column(String)
    posted_date = Column(String)

    description = Column(String)

    url = Column(String, unique=True)

    match_score = Column(Integer)

    status = Column(String, default="New")