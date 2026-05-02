from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class AIUsageRecord(Base):
    __tablename__ = "ai_usage_records"

    id = Column(String(36), primary_key=True)
    team_id = Column(String(36), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    provider = Column(String(50), nullable=False)
    model = Column(String(80), nullable=False)
    tokens_input = Column(Integer, default=0)
    tokens_output = Column(Integer, default=0)
    total_requests = Column(Integer, default=0)
    code_generation_requests = Column(Integer, default=0)
    documentation_requests = Column(Integer, default=0)
    review_requests = Column(Integer, default=0)
    debugging_requests = Column(Integer, default=0)
    total_cost_usd = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship("Team", back_populates="ai_usage")


class AITokenCost(Base):
    __tablename__ = "ai_token_costs"

    id = Column(String(36), primary_key=True)
    provider = Column(String(50), nullable=False)
    model = Column(String(80), nullable=False)
    cost_per_1k_input = Column(Float, nullable=False)
    cost_per_1k_output = Column(Float, nullable=False)
    effective_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
