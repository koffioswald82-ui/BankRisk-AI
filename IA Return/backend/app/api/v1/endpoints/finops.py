from fastapi import APIRouter
from typing import Optional
from datetime import date

from ....services.data_store import get_teams, get_sprint_metrics, get_deployment_metrics, get_quality_metrics, get_ai_usage
from ....services.analytics_engine import aggregate_team_kpis
from ....services.finops_engine import (
    calculate_operational_savings, build_roi_scenarios,
    run_monte_carlo, forecast_ai_costs, calculate_cost_breakdown,
    generate_finops_recommendations,
)

router = APIRouter(prefix="/finops", tags=["FinOps"])


@router.get("/snapshot")
async def get_finops_snapshot():
    teams = get_teams()
    sprints = get_sprint_metrics()
    deployments = get_deployment_metrics()
    quality = get_quality_metrics()
    ai_usage = get_ai_usage()

    kpis = aggregate_team_kpis(teams, sprints, deployments, quality, ai_usage)
    if not kpis:
        return {}

    enriched = []
    for k in kpis:
        k["productivity_boost_hours"] = k.get("avg_velocity", 0) * 0.28
        k["bugs_prevented"] = max(0, 4 - k.get("bug_rate", 4))
        k["incidents_prevented"] = max(0, 3 - k.get("incidents_count", 0) / 12)
        k["doc_hours_saved"] = 3.5 * k.get("ai_adoption_rate", 0) / 100
        enriched.append(k)

    savings = calculate_operational_savings(enriched)
    return savings


@router.get("/roi/scenarios")
async def get_roi_scenarios():
    teams = get_teams()
    ai_usage = get_ai_usage()
    sprints = get_sprint_metrics()
    deployments = get_deployment_metrics()
    quality = get_quality_metrics()

    kpis = aggregate_team_kpis(teams, sprints, deployments, quality, ai_usage)
    total_cost = sum(k.get("ai_cost_usd", 0) for k in kpis)
    total_engineers = sum(k.get("team_size", 0) for k in kpis)
    avg_velocity = sum(k.get("avg_velocity", 0) for k in kpis) / max(len(kpis), 1)
    base_savings = avg_velocity * 0.28 * total_engineers * 125 * 12

    return build_roi_scenarios(base_savings, total_cost)


@router.get("/montecarlo")
async def get_monte_carlo(simulations: int = 5000):
    teams = get_teams()
    ai_usage = get_ai_usage()
    sprints = get_sprint_metrics()
    deployments = get_deployment_metrics()
    quality = get_quality_metrics()

    kpis = aggregate_team_kpis(teams, sprints, deployments, quality, ai_usage)
    total_cost = sum(k.get("ai_cost_usd", 0) for k in kpis)
    total_engineers = sum(k.get("team_size", 0) for k in kpis)
    avg_velocity = sum(k.get("avg_velocity", 0) for k in kpis) / max(len(kpis), 1)
    base_savings = avg_velocity * 0.28 * total_engineers * 125 * 12

    return run_monte_carlo(base_savings, total_cost, simulations)


@router.get("/forecast/costs")
async def get_cost_forecast(forecast_months: int = 6):
    ai_usage = get_ai_usage()
    if not ai_usage:
        return []

    import pandas as pd
    df = pd.DataFrame(ai_usage)
    df["period_start"] = pd.to_datetime(df["period_start"])
    monthly = df.groupby(df["period_start"].dt.to_period("M"))["total_cost_usd"].sum().reset_index()
    monthly = monthly.sort_values("period_start")
    costs = monthly["total_cost_usd"].tolist()

    return forecast_ai_costs(costs, forecast_months)


@router.get("/cost-breakdown")
async def get_cost_breakdown():
    ai_usage = get_ai_usage()
    return calculate_cost_breakdown(ai_usage)


@router.get("/recommendations")
async def get_recommendations():
    teams = get_teams()
    sprints = get_sprint_metrics()
    deployments = get_deployment_metrics()
    quality = get_quality_metrics()
    ai_usage = get_ai_usage()

    kpis = aggregate_team_kpis(teams, sprints, deployments, quality, ai_usage)
    cost_breakdown = calculate_cost_breakdown(ai_usage)
    return generate_finops_recommendations(kpis, cost_breakdown)
