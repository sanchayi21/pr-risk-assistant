from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    github_repo_id = Column(Integer, unique=True, nullable=False)
    owner = Column(String, nullable=False)       # e.g. "sanchayi"
    name = Column(String, nullable=False)        # e.g. "my-project"
    created_at = Column(DateTime, default=datetime.utcnow)

    pull_requests = relationship("PullRequest", back_populates="repository")


class PullRequest(Base):
    __tablename__ = "pull_requests"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    pr_number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    status = Column(String, default="open")      # open, closed, merged
    created_at = Column(DateTime, default=datetime.utcnow)

    repository = relationship("Repository", back_populates="pull_requests")
    review = relationship("Review", back_populates="pull_request", uselist=False)


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    pr_id = Column(Integer, ForeignKey("pull_requests.id"), nullable=False)
    summary = Column(Text, nullable=False)        # AI's overall summary
    risk_score = Column(Float, nullable=False)    # 1.0 to 10.0
    bugs = Column(Text, nullable=True)            # AI found bugs
    security_issues = Column(Text, nullable=True) # AI found security problems
    test_gaps = Column(Text, nullable=True)       # AI found missing tests
    created_at = Column(DateTime, default=datetime.utcnow)

    pull_request = relationship("PullRequest", back_populates="review")