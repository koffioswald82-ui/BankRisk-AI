from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum


class InsightSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class InsightCategory(str, Enum):
    COST_ANOMALY = "cost_anomaly"
    PERFORMANCE_GAP = "performance_gap"
    AI_OPTIMIZATION = "ai_optimization"
    QUALITY_RISK = "quality_risk"
    VELOCITY_INSIGHT = "velocity_insight"
    FINOPS = "finops"
    GOVERNANCE = "governance"


class StrategicInsight(BaseModel):
    id: str
    severity: InsightSeverity
    category: InsightCategory
    title: str
    description: str
    team_name: Optional[str] = None
    metric_value: Optional[float] = None
    benchmark_value: Optional[float] = None
    delta_pct: Optional[float] = None
    recommended_action: str
    estimated_impact_usd: Optional[float] = None
    confidence_score: float
    generated_at: datetime


class InsightsSummary(BaseModel):
    total_insights: int
    critical_count: int
    high_count: int
    medium_count: int
    total_opportunity_usd: float
    insights: List[StrategicInsight]


class ExecutiveBriefing(BaseModel):
    headline: str
    period: str
    key_wins: List[str]
    risks: List[str]
    recommendations: List[str]
    financial_summary: str
    ai_maturity_score: float
