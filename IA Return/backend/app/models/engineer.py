from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Engineer(Base):
    __tablename__ = "engineers"

    id = Column(String(36), primary_key=True)
    team_id = Column(String(36), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    seniority = Column(String(20), nullable=False)
    role = Column(String(80), nullable=False)
    ai_enabled = Column(Boolean, default=True)
    ai_adoption_score = Column(Float, default=0.0)
    joined_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship("Team", back_populates="engineers")
