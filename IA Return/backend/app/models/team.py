from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..core.database import Base


class TeamDomain(str, enum.Enum):
    PLATFORM = "Platform Engineering"
    DATA = "Data & AI"
    FRONTEND = "Frontend"
    BACKEND = "Backend"
    DEVOPS = "DevOps & SRE"
    SECURITY = "Security"
    MOBILE = "Mobile"
    ANALYTICS = "Analytics"


class Team(Base):
    __tablename__ = "teams"

    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    domain = Column(String(50), nullable=False)
    size = Column(Integer, nullable=False)
    department = Column(String(100))
    lead_engineer = Column(String(100))
    ai_adoption_tier = Column(String(20), default="standard")
    budget_usd = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    engineers = relationship("Engineer", back_populates="team", cascade="all, delete-orphan")
    sprint_metrics = relationship("SprintMetric", back_populates="team", cascade="all, delete-orphan")
    deployment_metrics = relationship("DeploymentMetric", back_populates="team", cascade="all, delete-orphan")
    quality_metrics = relationship("QualityMetric", back_populates="team", cascade="all, delete-orphan")
    ai_usage = relationship("AIUsageRecord", back_populates="team", cascade="all, delete-orphan")
