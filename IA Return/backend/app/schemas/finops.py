from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import date


class ROIScenario(BaseModel):
    scenario_name: str
    label: str
    roi_pct: float
    net_benefit_usd: float
    break_even_months: float
    cumulative_savings_12m: float
    probability: float


class FinOpsSnapshot(BaseModel):
    total_ai_spend_usd: float
    total_operational_savings_usd: float
    net_roi_usd: float
    roi_pct: float
    cost_per_engineer_usd: float
    cost_per_story_point_usd: float
    efficiency_ratio: float
    break_even_months: float
    budget_variance_pct: float
    projected_annual_spend_usd: float


class ForecastPoint(BaseModel):
    period: str
    actual: Optional[float] = None
    forecast: float
    lower_bound: float
    upper_bound: float


class CostBreakdown(BaseModel):
    category: str
    amount_usd: float
    percentage: float
    trend_pct: float


class MonteCarloResult(BaseModel):
    simulation_count: int
    mean_roi_pct: float
    median_roi_pct: float
    std_deviation: float
    p10_roi_pct: float
    p50_roi_pct: float
    p90_roi_pct: float
    probability_positive_roi: float
    distribution: List[float]


class FinOpsRecommendation(BaseModel):
    id: str
    priority: str
    category: str
    title: str
    description: str
    estimated_savings_usd: float
    implementation_effort: str
    impact_score: float
