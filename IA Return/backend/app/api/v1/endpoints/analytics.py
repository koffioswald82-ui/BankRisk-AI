from fastapi import APIRouter, Query
from typing import Optional
from datetime import date

from ....services.data_store import (
    get_teams, get_sprint_metrics, get_deployment_metrics,
    get_quality_metrics, get_ai_usage,
)
from ....services.analytics_engine import (
    aggregate_team_kpis, build_time_series, calculate_platform_overview,
    build_heatmap_data, build_radar_data,
)
import pandas as pd

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def _default_period():
    return date(2024, 1, 1), date(2024, 12, 31)


@router.get("/overview")
async def get_platform_overview(
    period_start: Optional[date] = Query(default=None),
    period_end: Optional[date] = Query(default=None),
):
    ps, pe = period_start or _default_period()[0], period_end or _default_period()[1]
    teams = get_teams()
    sprints = get_sprint_metrics(period_start=ps)
    deployments = get_deployment_metrics(period_start=ps)
    quality = get_quality_metrics(period_start=ps)
    ai_usage = get_ai_usage(period_start=ps)

    kpis = aggregate_team_kpis(teams, sprints, deployments, quality, ai_usage, ps, pe)
    overview = calculate_platform_overview(kpis, ps, pe)
    return overview


@router.get("/teams/kpis")
async def get_all_team_kpis(
    period_start: Optional[date] = Query(default=None),
    period_end: Optional[date] = Query(default=None),
):
    ps, pe = period_start or _default_period()[0], period_end or _default_period()[1]
    teams = get_teams()
    sprints = get_sprint_metrics(period_start=ps)
    deployments = get_deployment_metrics(period_start=ps)
    quality = get_quality_metrics(period_start=ps)
    ai_usage = get_ai_usage(period_start=ps)

    kpis = aggregate_team_kpis(teams, sprints, deployments, quality, ai_usage, ps, pe)
    return {"teams": kpis, "total": len(kpis)}


@router.get("/teams/{team_id}/kpis")
async def get_single_team_kpis(team_id: str):
    teams = [t for t in get_teams() if t["id"] == team_id]
    if not teams:
        return {"error": "Team not found"}

    sprints = get_sprint_metrics(team_id=team_id)
    deployments = get_deployment_metrics(team_id=team_id)
    quality = get_quality_metrics(team_id=team_id)
    ai_usage = get_ai_usage(team_id=team_id)

    kpis = aggregate_team_kpis(teams, sprints, deployments, quality, ai_usage)
    return kpis[0] if kpis else {}


@router.get("/timeseries/velocity")
async def get_velocity_timeseries():
    teams = get_teams()
    sprints = get_sprint_metrics()
    df = pd.DataFrame(sprints)
    return build_time_series("velocity", teams, df)


@router.get("/timeseries/quality")
async def get_quality_timeseries():
    teams = get_teams()
    quality = get_quality_metrics()
    df = pd.DataFrame(quality)
    return build_time_series("code_quality_score", teams, df)


@router.get("/timeseries/ai-cost")
async def get_ai_cost_timeseries():
    teams = get_teams()
    ai_usage = get_ai_usage()
    df = pd.DataFrame(ai_usage)
    return build_time_series("total_cost_usd", teams, df)


@router.get("/timeseries/tokens")
async def get_token_timeseries():
    teams = get_teams()
    ai_usage = get_ai_usage()
    if not ai_usage:
        return []
    df = pd.DataFrame(ai_usage)
    df["total_tokens"] = df["tokens_input"] + df["tokens_output"]
    return build_time_series("total_tokens", teams, df)


@router.get("/heatmap")
async def get_kpi_heatmap():
    teams = get_teams()
    sprints = get_sprint_metrics()
    deployments = get_deployment_metrics()
    quality = get_quality_metrics()
    ai_usage = get_ai_usage()
    kpis = aggregate_team_kpis(teams, sprints, deployments, quality, ai_usage)
    return build_heatmap_data(kpis)


@router.get("/radar")
async def get_team_radar():
    teams = get_teams()
    sprints = get_sprint_metrics()
    deployments = get_deployment_metrics()
    quality = get_quality_metrics()
    ai_usage = get_ai_usage()
    kpis = aggregate_team_kpis(teams, sprints, deployments, quality, ai_usage)
    return build_radar_data(kpis)


@router.get("/rankings")
async def get_team_rankings():
    teams = get_teams()
    sprints = get_sprint_metrics()
    deployments = get_deployment_metrics()
    quality = get_quality_metrics()
    ai_usage = get_ai_usage()
    kpis = aggregate_team_kpis(teams, sprints, deployments, quality, ai_usage)
    ranked = sorted(kpis, key=lambda x: x.get("aovi_score", 0), reverse=True)
    return {"rankings": ranked}
