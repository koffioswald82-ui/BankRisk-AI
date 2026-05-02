from fastapi import APIRouter

from ....services.data_store import get_teams, get_sprint_metrics, get_deployment_metrics, get_quality_metrics, get_ai_usage
from ....services.analytics_engine import aggregate_team_kpis, calculate_platform_overview
from ....services.insights_generator import generate_insights, generate_executive_briefing
from datetime import date

router = APIRouter(prefix="/insights", tags=["Insights"])


@router.get("/strategic")
async def get_strategic_insights():
    teams = get_teams()
    sprints = get_sprint_metrics()
    deployments = get_deployment_metrics()
    quality = get_quality_metrics()
    ai_usage = get_ai_usage()

    kpis = aggregate_team_kpis(teams, sprints, deployments, quality, ai_usage)
    return generate_insights(kpis)


@router.get("/executive-briefing")
async def get_executive_briefing():
    ps, pe = date(2024, 1, 1), date(2024, 12, 31)
    teams = get_teams()
    sprints = get_sprint_metrics()
    deployments = get_deployment_metrics()
    quality = get_quality_metrics()
    ai_usage = get_ai_usage()

    kpis = aggregate_team_kpis(teams, sprints, deployments, quality, ai_usage)
    overview = calculate_platform_overview(kpis, ps, pe)
    insights_summary = generate_insights(kpis)
    return generate_executive_briefing(overview, kpis, insights_summary)
