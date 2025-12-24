from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base
import datetime

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    url = Column(String, nullable=False)
    status = Column(String, default="pending") # pending, crawling, analyzing, completed, failed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    options = Column(JSON, nullable=True)
    error = Column(String, nullable=True)

    keywords = relationship("Keyword", back_populates="job", cascade="all, delete-orphan")

class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("jobs.id"))
    phrase = Column(String, index=True)
    score = Column(Float)
    occurrences = Column(Integer)
    pages_count = Column(Integer)
    top_page = Column(String)
    source_mix = Column(JSON) # {title: X, h1: Y, ...}
    intent = Column(String)
    language = Column(String)

    job = relationship("Job", back_populates="keywords")
