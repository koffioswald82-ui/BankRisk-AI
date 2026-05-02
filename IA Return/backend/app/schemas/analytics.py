from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date


class TeamKPISummary(BaseModel):
    team_id: str
    team_name: str
    domain: str
    team_size: int
    avg_velocity: float
    story_points_delivered: float
    avg_dev_time_hours: float
    bug_rate: float
    test_coverage_pct: float
    code_quality_score: float
    deployment_frequency: float
    change_failure_rate: float
    ai_adoption_rate: float
    tokens_consumed: int
    ai_cost_usd: float
    cost_per_engineer: float
    aovi_score: float
    aovi_rank: int
    productivity_index: float
    quality_index: float
    velocity_index: float


class PlatformOverview(BaseModel):
    total_teams: int
    total_engineers: int
    total_ai_cost_usd: float
    total_tokens_consumed: int
    avg_productivity_gain_pct: float
    avg_quality_improvement_pct: float
    global_ai_adoption_rate: float
    estimated_savings_usd: float
    global_roi_pct: float
    avg_aovi_score: float
    period_start: date
    period_end: date


class TimeSeriesPoint(BaseModel):
    period: str
    value: float
    label: Optional[str] = None


class TeamTrendData(BaseModel):
    team_id: str
    team_name: str
    series: List[TimeSeriesPoint]


class HeatmapCell(BaseModel):
    team: str
    metric: str
    value: float
    normalized: float


class RadarDataPoint(BaseModel):
    metric: str
    value: float
    fullMark: float = 100


class TeamRadarData(BaseModel):
    team_id: str
    team_name: str
    data: List[RadarDataPoint]
