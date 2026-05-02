"""
In-memory data store for demo/simulation mode.
Loads synthetic data once at startup for fast API responses without PostgreSQL.
"""
from typing import Dict, Any, List, Optional
from datetime import date
import threading

from ..data.generators.synthetic_data import build_full_dataset

_lock = threading.Lock()
_store: Dict[str, Any] = {}
_initialized = False


def initialize_store(months: int = 12) -> None:
    global _store, _initialized
    with _lock:
        if not _initialized:
            _store = build_full_dataset(months=months)
            _initialized = True


def get_teams() -> List[Dict]:
    return _store.get("teams", [])


def get_engineers() -> List[Dict]:
    return _store.get("engineers", [])


def get_sprint_metrics(
    team_id: Optional[str] = None,
    period_start: Optional[date] = None,
    period_end: Optional[date] = None,
) -> List[Dict]:
    records = _store.get("sprint_metrics", [])
    if team_id:
        records = [r for r in records if r["team_id"] == team_id]
    if period_start:
        records = [r for r in records if r["period_start"] >= period_start]
    if period_end:
        records = [r for r in records if r["period_start"] <= period_end]
    return records


def get_deployment_metrics(
    team_id: Optional[str] = None,
    period_start: Optional[date] = None,
) -> List[Dict]:
    records = _store.get("deployment_metrics", [])
    if team_id:
        records = [r for r in records if r["team_id"] == team_id]
    if period_start:
        records = [r for r in records if r["period_start"] >= period_start]
    return records


def get_quality_metrics(
    team_id: Optional[str] = None,
    period_start: Optional[date] = None,
) -> List[Dict]:
    records = _store.get("quality_metrics", [])
    if team_id:
        records = [r for r in records if r["team_id"] == team_id]
    if period_start:
        records = [r for r in records if r["period_start"] >= period_start]
    return records


def get_ai_usage(
    team_id: Optional[str] = None,
    period_start: Optional[date] = None,
) -> List[Dict]:
    records = _store.get("ai_usage_records", [])
    if team_id:
        records = [r for r in records if r["team_id"] == team_id]
    if period_start:
        records = [r for r in records if r["period_start"] >= period_start]
    return records
