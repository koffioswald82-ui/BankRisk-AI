"""
Enterprise Synthetic Data Generator
Produces realistic multi-team, multi-month engineering + AI usage datasets.
"""
import uuid
import random
import numpy as np
from datetime import date, timedelta
from typing import List, Dict, Any
from faker import Faker

fake = Faker()
random.seed(42)
np.random.seed(42)

TEAMS_CONFIG = [
    {"name": "Team Alpha",    "domain": "Platform Engineering", "size": 10, "ai_tier": "pioneer",  "budget": 85000,  "base_velocity": 95},
    {"name": "Team Beta",     "domain": "Data & AI",            "size": 8,  "ai_tier": "pioneer",  "budget": 72000,  "base_velocity": 88},
    {"name": "Team Gamma",    "domain": "Backend",              "size": 9,  "ai_tier": "advanced",  "budget": 68000,  "base_velocity": 82},
    {"name": "Team Delta",    "domain": "Frontend",             "size": 7,  "ai_tier": "standard",  "budget": 55000,  "base_velocity": 74},
    {"name": "Team Epsilon",  "domain": "DevOps & SRE",         "size": 6,  "ai_tier": "advanced",  "budget": 62000,  "base_velocity": 79},
    {"name": "Team Zeta",     "domain": "Security",             "size": 5,  "ai_tier": "standard",  "budget": 48000,  "base_velocity": 68},
    {"name": "Team Eta",      "domain": "Mobile",               "size": 8,  "ai_tier": "advanced",  "budget": 61000,  "base_velocity": 77},
    {"name": "Team Theta",    "domain": "Analytics",            "size": 7,  "ai_tier": "pioneer",  "budget": 70000,  "base_velocity": 84},
    {"name": "Team Iota",     "domain": "Backend",              "size": 9,  "ai_tier": "standard",  "budget": 57000,  "base_velocity": 70},
    {"name": "Team Kappa",    "domain": "Frontend",             "size": 6,  "ai_tier": "lagging",   "budget": 42000,  "base_velocity": 58},
    {"name": "Team Lambda",   "domain": "Data & AI",            "size": 8,  "ai_tier": "advanced",  "budget": 66000,  "base_velocity": 80},
    {"name": "Team Mu",       "domain": "DevOps & SRE",         "size": 5,  "ai_tier": "lagging",   "budget": 40000,  "base_velocity": 54},
]

AI_TIER_PARAMS = {
    "pioneer":  {"adoption": 0.91, "token_multiplier": 1.5, "productivity_boost": 0.38, "quality_boost": 0.28},
    "advanced": {"adoption": 0.72, "token_multiplier": 1.1, "productivity_boost": 0.24, "quality_boost": 0.18},
    "standard": {"adoption": 0.50, "token_multiplier": 0.8, "productivity_boost": 0.13, "quality_boost": 0.10},
    "lagging":  {"adoption": 0.28, "token_multiplier": 0.5, "productivity_boost": 0.05, "quality_boost": 0.03},
}

SENIORITY_LEVELS = ["Junior", "Mid-level", "Senior", "Staff", "Principal"]
ROLES = [
    "Software Engineer", "Senior Software Engineer", "Staff Engineer",
    "Data Engineer", "ML Engineer", "DevOps Engineer", "SRE",
    "Frontend Engineer", "Full Stack Engineer", "Security Engineer",
    "Platform Engineer", "Analytics Engineer",
]
AI_PROVIDERS = [
    {"provider": "OpenAI", "model": "gpt-4o", "cost_input": 0.005, "cost_output": 0.015},
    {"provider": "Anthropic", "model": "claude-3-5-sonnet", "cost_input": 0.003, "cost_output": 0.015},
    {"provider": "OpenAI", "model": "gpt-4o-mini", "cost_input": 0.00015, "cost_output": 0.0006},
]


def _growth_curve(month: int, boost: float) -> float:
    return 1.0 + boost * (1 - np.exp(-0.35 * month))


def generate_teams() -> List[Dict[str, Any]]:
    teams = []
    for cfg in TEAMS_CONFIG:
        teams.append({
            "id": str(uuid.uuid4()),
            "name": cfg["name"],
            "domain": cfg["domain"],
            "size": cfg["size"],
            "department": "Engineering",
            "lead_engineer": fake.name(),
            "ai_adoption_tier": cfg["ai_tier"],
            "budget_usd": cfg["budget"],
        })
    return teams


def generate_engineers(teams: List[Dict]) -> List[Dict[str, Any]]:
    engineers = []
    for team in teams:
        for _ in range(team["size"]):
            seniority = random.choices(
                SENIORITY_LEVELS, weights=[15, 30, 35, 15, 5]
            )[0]
            tier_params = AI_TIER_PARAMS[team["ai_adoption_tier"]]
            engineers.append({
                "id": str(uuid.uuid4()),
                "team_id": team["id"],
                "name": fake.name(),
                "seniority": seniority,
                "role": random.choice(ROLES),
                "ai_enabled": random.random() < tier_params["adoption"],
                "ai_adoption_score": round(random.gauss(tier_params["adoption"] * 85, 10), 1),
                "joined_at": fake.date_between(start_date="-3y", end_date="-1m"),
            })
    return engineers


def generate_sprint_metrics(teams: List[Dict], months: int = 12) -> List[Dict[str, Any]]:
    records = []
    base_start = date(2024, 1, 1)

    for team in teams:
        cfg = next(c for c in TEAMS_CONFIG if c["name"] == team["name"])
        tier = AI_TIER_PARAMS[team["ai_adoption_tier"]]
        sprint_num = 1

        for m in range(months):
            period_start = base_start + timedelta(days=m * 30)
            period_end = period_start + timedelta(days=29)
            growth = _growth_curve(m, tier["productivity_boost"])
            noise = random.gauss(1.0, 0.06)

            planned = round(cfg["base_velocity"] * 2.2 * random.gauss(1, 0.08), 1)
            delivered = round(planned * random.gauss(0.87 * growth, 0.07), 1)
            velocity = round(delivered / max(team["size"], 1), 2)
            ai_assisted = int(delivered * tier["adoption"] * random.gauss(0.55, 0.08))

            records.append({
                "id": str(uuid.uuid4()),
                "team_id": team["id"],
                "sprint_number": sprint_num,
                "period_start": period_start,
                "period_end": period_end,
                "story_points_planned": planned,
                "story_points_delivered": delivered,
                "velocity": velocity,
                "avg_dev_time_hours": round(random.gauss(18 / growth, 2.5) * noise, 2),
                "commits_count": int(random.gauss(140 * growth, 20) * noise),
                "prs_merged": int(random.gauss(28 * growth, 5) * noise),
                "prs_rejected": int(random.gauss(4 / growth, 1.5)),
                "code_review_time_hours": round(random.gauss(3.2 / growth, 0.7), 2),
                "ai_assisted_tasks": ai_assisted,
            })
            sprint_num += 1

    return records


def generate_deployment_metrics(teams: List[Dict], months: int = 12) -> List[Dict[str, Any]]:
    records = []
    base_start = date(2024, 1, 1)

    for team in teams:
        tier = AI_TIER_PARAMS[team["ai_adoption_tier"]]
        for m in range(months):
            period_start = base_start + timedelta(days=m * 30)
            period_end = period_start + timedelta(days=29)
            growth = _growth_curve(m, tier["quality_boost"])
            total = int(random.gauss(18 * growth, 4))
            failed = max(0, int(total * random.gauss(0.06 / growth, 0.02)))
            successful = total - failed

            records.append({
                "id": str(uuid.uuid4()),
                "team_id": team["id"],
                "period_start": period_start,
                "period_end": period_end,
                "deployments_total": total,
                "deployments_successful": successful,
                "deployments_failed": failed,
                "deployment_frequency_per_week": round(total / 4.3, 2),
                "lead_time_hours": round(random.gauss(26 / growth, 5), 2),
                "mttr_hours": round(random.gauss(1.8 / growth, 0.5), 2),
                "change_failure_rate": round(failed / max(total, 1) * 100, 2),
                "incidents_count": max(0, int(random.gauss(3 / growth, 1))),
            })

    return records


def generate_quality_metrics(teams: List[Dict], months: int = 12) -> List[Dict[str, Any]]:
    records = []
    base_start = date(2024, 1, 1)

    for team in teams:
        tier = AI_TIER_PARAMS[team["ai_adoption_tier"]]
        for m in range(months):
            period_start = base_start + timedelta(days=m * 30)
            period_end = period_start + timedelta(days=29)
            growth = _growth_curve(m, tier["quality_boost"])
            quality_score = min(100, round(random.gauss(68 * growth, 6), 1))
            coverage = min(100, round(random.gauss(62 * growth, 8), 1))
            doc_coverage = min(100, round(random.gauss(55 * growth, 10), 1))

            records.append({
                "id": str(uuid.uuid4()),
                "team_id": team["id"],
                "period_start": period_start,
                "period_end": period_end,
                "bug_rate_per_kloc": round(random.gauss(1.8 / growth, 0.4), 3),
                "bugs_opened": int(random.gauss(18 / growth, 4)),
                "bugs_closed": int(random.gauss(20 * growth, 5)),
                "critical_bugs": max(0, int(random.gauss(2 / growth, 1))),
                "test_coverage_pct": coverage,
                "code_quality_score": quality_score,
                "technical_debt_hours": round(random.gauss(45 / growth, 10), 1),
                "documentation_coverage_pct": doc_coverage,
            })

    return records


def generate_ai_usage(teams: List[Dict], months: int = 12) -> List[Dict[str, Any]]:
    records = []
    base_start = date(2024, 1, 1)

    for team in teams:
        cfg = next(c for c in TEAMS_CONFIG if c["name"] == team["name"])
        tier = AI_TIER_PARAMS[team["ai_adoption_tier"]]
        provider_info = random.choice(AI_PROVIDERS)

        for m in range(months):
            period_start = base_start + timedelta(days=m * 30)
            period_end = period_start + timedelta(days=29)
            growth = _growth_curve(m, 0.22)
            # Enterprise-scale token volumes: ~20K requests/month × ~6K tokens each
            base_tokens = 120_000_000 * tier["token_multiplier"] * cfg["size"] / 8

            tokens_input = int(random.gauss(base_tokens * growth, base_tokens * 0.12))
            tokens_output = int(tokens_input * random.gauss(0.35, 0.04))
            requests = int(random.gauss(1800 * tier["adoption"] * growth, 200))
            cost = (tokens_input / 1000 * provider_info["cost_input"]
                    + tokens_output / 1000 * provider_info["cost_output"])

            records.append({
                "id": str(uuid.uuid4()),
                "team_id": team["id"],
                "period_start": period_start,
                "period_end": period_end,
                "provider": provider_info["provider"],
                "model": provider_info["model"],
                "tokens_input": max(0, tokens_input),
                "tokens_output": max(0, tokens_output),
                "total_requests": max(0, requests),
                "code_generation_requests": int(requests * 0.42),
                "documentation_requests": int(requests * 0.18),
                "review_requests": int(requests * 0.22),
                "debugging_requests": int(requests * 0.18),
                "total_cost_usd": round(max(0, cost), 4),
            })

    return records


def build_full_dataset(months: int = 12) -> Dict[str, Any]:
    teams = generate_teams()
    engineers = generate_engineers(teams)
    sprints = generate_sprint_metrics(teams, months)
    deployments = generate_deployment_metrics(teams, months)
    quality = generate_quality_metrics(teams, months)
    ai_usage = generate_ai_usage(teams, months)

    return {
        "teams": teams,
        "engineers": engineers,
        "sprint_metrics": sprints,
        "deployment_metrics": deployments,
        "quality_metrics": quality,
        "ai_usage_records": ai_usage,
    }
