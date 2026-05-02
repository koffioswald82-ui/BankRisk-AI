from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class SprintMetric(Base):
    __tablename__ = "sprint_metrics"

    id = Column(String(36), primary_key=True)
    team_id = Column(String(36), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    sprint_number = Column(Integer, nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    story_points_planned = Column(Float, default=0)
    story_points_delivered = Column(Float, default=0)
    velocity = Column(Float, default=0)
    avg_dev_time_hours = Column(Float, default=0)
    commits_count = Column(Integer, default=0)
    prs_merged = Column(Integer, default=0)
    prs_rejected = Column(Integer, default=0)
    code_review_time_hours = Column(Float, default=0)
    ai_assisted_tasks = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship("Team", back_populates="sprint_metrics")


class DeploymentMetric(Base):
    __tablename__ = "deployment_metrics"

    id = Column(String(36), primary_key=True)
    team_id = Column(String(36), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    deployments_total = Column(Integer, default=0)
    deployments_successful = Column(Integer, default=0)
    deployments_failed = Column(Integer, default=0)
    deployment_frequency_per_week = Column(Float, default=0)
    lead_time_hours = Column(Float, default=0)
    mttr_hours = Column(Float, default=0)
    change_failure_rate = Column(Float, default=0)
    incidents_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship("Team", back_populates="deployment_metrics")


class QualityMetric(Base):
    __tablename__ = "quality_metrics"

    id = Column(String(36), primary_key=True)
    team_id = Column(String(36), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    bug_rate_per_kloc = Column(Float, default=0)
    bugs_opened = Column(Integer, default=0)
    bugs_closed = Column(Integer, default=0)
    critical_bugs = Column(Integer, default=0)
    test_coverage_pct = Column(Float, default=0)
    code_quality_score = Column(Float, default=0)
    technical_debt_hours = Column(Float, default=0)
    documentation_coverage_pct = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship("Team", back_populates="quality_metrics")
