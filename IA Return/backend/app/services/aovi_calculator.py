"""
AI Operational Value Index (AOVI) Calculator
Proprietary scoring model: AOVI = (Productivity × Quality × Velocity) / AI_Cost
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any
from sklearn.preprocessing import MinMaxScaler


AOWI_WEIGHTS = {
    "productivity": 0.35,
    "quality": 0.30,
    "velocity": 0.25,
    "ai_efficiency": 0.10,
}

PRODUCTIVITY_METRICS = [
    "story_points_delivered",
    "commits_count",
    "prs_merged",
    "ai_assisted_tasks",
]

QUALITY_METRICS = [
    "code_quality_score",
    "test_coverage_pct",
    "documentation_coverage_pct",
]

QUALITY_INVERSE_METRICS = [
    "bug_rate_per_kloc",
    "change_failure_rate",
    "critical_bugs",
]

VELOCITY_METRICS = [
    "velocity",
    "deployment_frequency_per_week",
]

VELOCITY_INVERSE_METRICS = [
    "avg_dev_time_hours",
    "lead_time_hours",
    "mttr_hours",
]


def normalize_series(series: pd.Series, inverse: bool = False) -> pd.Series:
    vals = series.values.reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0.01, 1.0))
    normalized = scaler.fit_transform(vals).flatten()
    if inverse:
        normalized = 1.0 - normalized + 0.01
    return pd.Series(normalized, index=series.index)


def calculate_aovi(team_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not team_data:
        return []

    df = pd.DataFrame(team_data)

    productivity_components = []
    for m in PRODUCTIVITY_METRICS:
        if m in df.columns:
            productivity_components.append(normalize_series(df[m]))

    quality_components = []
    for m in QUALITY_METRICS:
        if m in df.columns:
            quality_components.append(normalize_series(df[m]))
    for m in QUALITY_INVERSE_METRICS:
        if m in df.columns:
            quality_components.append(normalize_series(df[m], inverse=True))

    velocity_components = []
    for m in VELOCITY_METRICS:
        if m in df.columns:
            velocity_components.append(normalize_series(df[m]))
    for m in VELOCITY_INVERSE_METRICS:
        if m in df.columns:
            velocity_components.append(normalize_series(df[m], inverse=True))

    prod_index = pd.concat(productivity_components, axis=1).mean(axis=1) if productivity_components else pd.Series([0.5] * len(df))
    qual_index = pd.concat(quality_components, axis=1).mean(axis=1) if quality_components else pd.Series([0.5] * len(df))
    vel_index = pd.concat(velocity_components, axis=1).mean(axis=1) if velocity_components else pd.Series([0.5] * len(df))

    numerator = (
        prod_index ** AOWI_WEIGHTS["productivity"]
        * qual_index ** AOWI_WEIGHTS["quality"]
        * vel_index ** AOWI_WEIGHTS["velocity"]
    )

    if "ai_cost_usd" in df.columns:
        cost_norm = normalize_series(df["ai_cost_usd"])
        denominator = cost_norm ** AOWI_WEIGHTS["ai_efficiency"]
    else:
        denominator = pd.Series([1.0] * len(df))

    raw_aovi = numerator / denominator
    scaler = MinMaxScaler(feature_range=(1, 100))
    aovi_scores = scaler.fit_transform(raw_aovi.values.reshape(-1, 1)).flatten()

    df["productivity_index"] = (prod_index * 100).round(2)
    df["quality_index"] = (qual_index * 100).round(2)
    df["velocity_index"] = (vel_index * 100).round(2)
    df["aovi_score"] = np.round(aovi_scores, 2)
    df["aovi_rank"] = df["aovi_score"].rank(ascending=False).astype(int)

    return df.to_dict(orient="records")


def get_team_performance_tier(aovi_score: float) -> str:
    if aovi_score >= 85:
        return "Elite"
    elif aovi_score >= 70:
        return "High Performer"
    elif aovi_score >= 50:
        return "Standard"
    elif aovi_score >= 30:
        return "Needs Improvement"
    else:
        return "Critical"


def generate_aovi_insights(ranked_teams: List[Dict]) -> List[str]:
    if not ranked_teams:
        return []

    sorted_teams = sorted(ranked_teams, key=lambda x: x.get("aovi_score", 0), reverse=True)
    insights = []

    if len(sorted_teams) >= 2:
        top = sorted_teams[0]
        bottom = sorted_teams[-1]
        gap = top.get("aovi_score", 0) - bottom.get("aovi_score", 0)
        insights.append(
            f"{top['team_name']} leads AOVI rankings with a score of {top['aovi_score']:.1f}, "
            f"outperforming {bottom['team_name']} by {gap:.1f} points."
        )

    for team in sorted_teams[:3]:
        prod = team.get("productivity_index", 0)
        cost = team.get("ai_cost_usd", 0)
        if prod > 75 and cost < team.get("avg_cost", cost * 1.1):
            insights.append(
                f"{team['team_name']} achieves {prod:.0f}/100 productivity with optimized AI spend — "
                f"a strong ROI signal."
            )

    for team in sorted_teams:
        if team.get("quality_index", 0) < 40:
            insights.append(
                f"Quality risk detected in {team['team_name']}: quality index at "
                f"{team.get('quality_index', 0):.0f}/100 — immediate action recommended."
            )

    return insights
