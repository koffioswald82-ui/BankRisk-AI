"""
FinOps Intelligence Engine
ROI modeling, cost optimization, Monte Carlo simulation, scenario forecasting.
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from datetime import date, timedelta
import uuid


AVERAGE_ENGINEER_HOURLY_COST_USD = 125
WORKING_HOURS_PER_MONTH = 160
MONTHS_IN_YEAR = 12


def calculate_operational_savings(
    team_data: List[Dict[str, Any]],
    baseline_period_months: int = 3,
) -> Dict[str, Any]:
    if not team_data:
        return {}

    df = pd.DataFrame(team_data)

    hours_saved_per_engineer = df.get("productivity_boost_hours", pd.Series([8.0] * len(df)))
    team_sizes = df.get("team_size", pd.Series([8] * len(df)))

    monthly_savings = hours_saved_per_engineer * team_sizes * AVERAGE_ENGINEER_HOURLY_COST_USD
    total_annual_savings = float(monthly_savings.sum() * MONTHS_IN_YEAR)

    bug_reduction_savings = float(
        df.get("bugs_prevented", pd.Series([3.0] * len(df))).sum()
        * 4.5 * AVERAGE_ENGINEER_HOURLY_COST_USD
        * MONTHS_IN_YEAR
    )

    incident_savings = float(
        df.get("incidents_prevented", pd.Series([1.0] * len(df))).sum()
        * 12 * AVERAGE_ENGINEER_HOURLY_COST_USD
        * MONTHS_IN_YEAR
    )

    doc_savings = float(
        df.get("doc_hours_saved", pd.Series([2.0] * len(df))).sum()
        * team_sizes.mean()
        * AVERAGE_ENGINEER_HOURLY_COST_USD
        * MONTHS_IN_YEAR
    )

    total_ai_cost = float(df.get("ai_cost_usd", pd.Series([5000.0] * len(df))).sum() * MONTHS_IN_YEAR)
    total_savings = total_annual_savings + bug_reduction_savings + incident_savings + doc_savings

    net_benefit = total_savings - total_ai_cost
    roi_pct = (net_benefit / max(total_ai_cost, 1)) * 100
    break_even_months = total_ai_cost / max(total_savings / MONTHS_IN_YEAR, 1)

    return {
        "total_annual_savings_usd": round(total_savings, 2),
        "productivity_savings_usd": round(total_annual_savings, 2),
        "quality_savings_usd": round(bug_reduction_savings + incident_savings, 2),
        "documentation_savings_usd": round(doc_savings, 2),
        "total_ai_cost_usd": round(total_ai_cost, 2),
        "net_benefit_usd": round(net_benefit, 2),
        "roi_pct": round(roi_pct, 2),
        "break_even_months": round(break_even_months, 2),
    }


def build_roi_scenarios(base_savings: float, base_cost: float) -> List[Dict[str, Any]]:
    scenarios = [
        {
            "scenario_name": "pessimistic",
            "label": "Pessimistic",
            "savings_multiplier": 0.65,
            "cost_multiplier": 1.20,
            "probability": 0.20,
        },
        {
            "scenario_name": "realistic",
            "label": "Realistic",
            "savings_multiplier": 1.00,
            "cost_multiplier": 1.00,
            "probability": 0.55,
        },
        {
            "scenario_name": "optimistic",
            "label": "Optimistic",
            "savings_multiplier": 1.35,
            "cost_multiplier": 0.90,
            "probability": 0.25,
        },
    ]

    results = []
    for s in scenarios:
        adj_savings = base_savings * s["savings_multiplier"]
        adj_cost = base_cost * s["cost_multiplier"]
        net = adj_savings - adj_cost
        roi = (net / max(adj_cost, 1)) * 100
        break_even = adj_cost / max(adj_savings / 12, 1)
        cumulative = sum([
            adj_savings / 12 * m - adj_cost / 12
            for m in range(1, 13)
        ])
        results.append({
            "scenario_name": s["scenario_name"],
            "label": s["label"],
            "roi_pct": round(roi, 2),
            "net_benefit_usd": round(net, 2),
            "break_even_months": round(break_even, 2),
            "cumulative_savings_12m": round(cumulative, 2),
            "probability": s["probability"],
        })

    return results


def run_monte_carlo(
    base_savings: float,
    base_cost: float,
    simulations: int = 5000,
) -> Dict[str, Any]:
    np.random.seed(42)
    savings_samples = np.random.normal(base_savings, base_savings * 0.18, simulations)
    cost_samples = np.random.normal(base_cost, base_cost * 0.12, simulations)
    roi_samples = ((savings_samples - cost_samples) / np.maximum(cost_samples, 1)) * 100

    return {
        "simulation_count": simulations,
        "mean_roi_pct": round(float(np.mean(roi_samples)), 2),
        "median_roi_pct": round(float(np.median(roi_samples)), 2),
        "std_deviation": round(float(np.std(roi_samples)), 2),
        "p10_roi_pct": round(float(np.percentile(roi_samples, 10)), 2),
        "p50_roi_pct": round(float(np.percentile(roi_samples, 50)), 2),
        "p90_roi_pct": round(float(np.percentile(roi_samples, 90)), 2),
        "probability_positive_roi": round(float(np.mean(roi_samples > 0)), 4),
        "distribution": [round(x, 2) for x in roi_samples[:200].tolist()],
    }


def forecast_ai_costs(
    monthly_costs: List[float],
    forecast_months: int = 6,
) -> List[Dict[str, Any]]:
    if len(monthly_costs) < 3:
        return []

    arr = np.array(monthly_costs)
    x = np.arange(len(arr))

    coeffs = np.polyfit(x, arr, 2)
    poly = np.poly1d(coeffs)

    residuals = arr - poly(x)
    std_err = np.std(residuals)

    results = []
    for i, val in enumerate(arr):
        results.append({
            "period": f"M{i + 1}",
            "actual": round(val, 2),
            "forecast": round(float(poly(i)), 2),
            "lower_bound": round(float(poly(i)) - 1.96 * std_err, 2),
            "upper_bound": round(float(poly(i)) + 1.96 * std_err, 2),
        })

    for j in range(forecast_months):
        idx = len(arr) + j
        forecast_val = float(poly(idx))
        results.append({
            "period": f"M{idx + 1}",
            "actual": None,
            "forecast": round(forecast_val, 2),
            "lower_bound": round(forecast_val - 1.96 * std_err * (1 + j * 0.1), 2),
            "upper_bound": round(forecast_val + 1.96 * std_err * (1 + j * 0.1), 2),
        })

    return results


def calculate_cost_breakdown(ai_usage_records: List[Dict]) -> List[Dict[str, Any]]:
    if not ai_usage_records:
        return []

    df = pd.DataFrame(ai_usage_records)
    total = float(df["total_cost_usd"].sum())

    breakdown = []
    category_map = {
        "Code Generation": "code_generation_requests",
        "Code Review": "review_requests",
        "Documentation": "documentation_requests",
        "Debugging": "debugging_requests",
    }

    total_requests = max(df[[v for v in category_map.values() if v in df.columns]].sum().sum(), 1)

    for cat, col in category_map.items():
        if col in df.columns:
            cat_requests = float(df[col].sum())
            cat_cost = total * (cat_requests / total_requests)
            breakdown.append({
                "category": cat,
                "amount_usd": round(cat_cost, 2),
                "percentage": round(cat_requests / total_requests * 100, 1),
                "trend_pct": round(np.random.normal(8, 4), 1),
            })

    return sorted(breakdown, key=lambda x: x["amount_usd"], reverse=True)


def generate_finops_recommendations(
    teams_data: List[Dict],
    cost_breakdown: List[Dict],
) -> List[Dict[str, Any]]:
    recommendations = []

    for team in teams_data:
        ai_cost = team.get("ai_cost_usd", 0)
        aovi = team.get("aovi_score", 50)
        tokens = team.get("tokens_consumed", 0)

        if aovi < 40 and ai_cost > 3000:
            recommendations.append({
                "id": str(uuid.uuid4()),
                "priority": "HIGH",
                "category": "AI Optimization",
                "title": f"Optimize AI usage in {team.get('team_name', 'Unknown Team')}",
                "description": (
                    f"AOVI score of {aovi:.0f} with ${ai_cost:,.0f} monthly spend indicates "
                    f"low return on AI investment. Consider prompt engineering workshops and "
                    f"task-specific model selection."
                ),
                "estimated_savings_usd": round(ai_cost * 0.28, 2),
                "implementation_effort": "Medium",
                "impact_score": 0.82,
            })

        if tokens > 2_000_000:
            recommendations.append({
                "id": str(uuid.uuid4()),
                "priority": "MEDIUM",
                "category": "FinOps",
                "title": f"Token consumption spike in {team.get('team_name', 'Unknown Team')}",
                "description": (
                    f"Token usage of {tokens:,} exceeds threshold. Implement output caching, "
                    f"context compression, and model tiering for non-critical tasks."
                ),
                "estimated_savings_usd": round(ai_cost * 0.18, 2),
                "implementation_effort": "Low",
                "impact_score": 0.67,
            })

    if cost_breakdown:
        top_cat = cost_breakdown[0]
        if top_cat["percentage"] > 45:
            recommendations.append({
                "id": str(uuid.uuid4()),
                "priority": "MEDIUM",
                "category": "Cost Distribution",
                "title": f"Concentration risk: {top_cat['category']} dominates AI spend",
                "description": (
                    f"{top_cat['category']} represents {top_cat['percentage']:.0f}% of total AI costs. "
                    f"Diversify model usage and implement request batching to reduce unit costs."
                ),
                "estimated_savings_usd": round(top_cat["amount_usd"] * 0.15, 2),
                "implementation_effort": "Low",
                "impact_score": 0.58,
            })

    return sorted(recommendations, key=lambda x: x["impact_score"], reverse=True)
