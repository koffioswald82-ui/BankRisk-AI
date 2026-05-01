"""
Business Impact Simulator — Cost Optimization Engine.

Combines fraud + credit results into a unified cost/savings dashboard.
Runs threshold sensitivity analysis to show how ROI changes with decision points.
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.config import (FRAUD_COST, CREDIT_COST, METRICS_DIR, REPORTS_DIR)


# ── Utility helpers ──────────────────────────────────────────────────────────

def _load_report(path: Path) -> dict | None:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


# ── Fraud cost simulation ────────────────────────────────────────────────────

def fraud_threshold_sweep(y_true: np.ndarray, y_prob: np.ndarray,
                           annual_tx: int | None = None) -> pd.DataFrame:
    """
    For a grid of thresholds, compute:
      - recall, precision, FP rate, FN rate
      - expected annual cost (FP * review_cost + FN * avg_fraud_amount)
      - annual savings vs legacy rule engine
    """
    from sklearn.metrics import confusion_matrix

    c   = FRAUD_COST
    atx = annual_tx or c["annual_tx_volume"]
    n   = len(y_true)

    records = []
    for t in np.linspace(0.01, 0.99, 100):
        y_pred = (y_prob >= t).astype(int)
        try:
            tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        except ValueError:
            continue

        scale  = atx / n
        precision = tp / (tp + fp + 1e-9)
        recall    = tp / (tp + fn + 1e-9)
        f1        = 2 * precision * recall / (precision + recall + 1e-9)

        ml_cost   = (fp * c["manual_review_cost"] + fn * c["avg_fraud_amount"]) * scale
        legacy_fp = int(atx * (1 - c["baseline_fraud_rate"]) * c["current_fp_rate"])
        legacy_fn = int(atx * c["baseline_fraud_rate"] * 0.15)
        legacy_cost = legacy_fp * c["manual_review_cost"] + legacy_fn * c["avg_fraud_amount"]
        savings   = legacy_cost - ml_cost

        records.append({
            "threshold":     round(t, 3),
            "precision":     round(precision, 4),
            "recall":        round(recall, 4),
            "f1":            round(f1, 4),
            "fp_alerts":     int(fp * scale),
            "fn_missed":     int(fn * scale),
            "annual_cost":   round(ml_cost, 0),
            "annual_savings":round(savings, 0),
            "roi_pct":       round(savings / (legacy_cost + 1e-9) * 100, 1),
        })

    return pd.DataFrame(records)


# ── Credit cost simulation ────────────────────────────────────────────────────

def credit_threshold_sweep(y_true: np.ndarray, y_prob: np.ndarray,
                            annual_apps: int = 50_000) -> pd.DataFrame:
    from sklearn.metrics import confusion_matrix

    c   = CREDIT_COST
    n   = len(y_true)
    loan, lgd = c["avg_loan_amount"], c["loss_given_default"]

    baseline_cost = int(annual_apps * c["baseline_default_rate"]) * loan * lgd
    records = []

    for t in np.linspace(0.01, 0.99, 100):
        y_pred = (y_prob >= t).astype(int)
        try:
            tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        except ValueError:
            continue

        scale     = annual_apps / n
        precision = tp / (tp + fp + 1e-9)
        recall    = tp / (tp + fn + 1e-9)
        f1        = 2 * precision * recall / (precision + recall + 1e-9)
        approval  = (tn + fp) / (n + 1e-9)    # approval rate

        ml_cost   = (fn * loan * lgd + fp * c["cost_per_rejected_good"]) * scale
        savings   = baseline_cost - ml_cost

        records.append({
            "threshold":     round(t, 3),
            "precision":     round(precision, 4),
            "recall":        round(recall, 4),
            "f1":            round(f1, 4),
            "approval_rate": round(approval, 4),
            "fn_approved_defaults": int(fn * scale),
            "fp_rejected_good":     int(fp * scale),
            "annual_cost":   round(ml_cost, 0),
            "annual_savings":round(savings, 0),
            "roi_pct":       round(savings / (baseline_cost + 1e-9) * 100, 1),
        })

    return pd.DataFrame(records)


# ── Combined business impact report ─────────────────────────────────────────

def build_combined_report(fraud_metrics: dict | None = None,
                           credit_metrics: dict | None = None) -> dict:
    """
    Combine fraud + credit savings into a top-level executive summary.
    Falls back to loading persisted JSON reports if metrics dicts not provided.
    """
    if fraud_metrics is None:
        fraud_metrics = _load_report(METRICS_DIR / "fraud_xgboost_smote_report.json")
    if credit_metrics is None:
        credit_metrics = _load_report(METRICS_DIR / "credit_xgboost_report.json")

    fraud_savings  = (fraud_metrics or {}).get("cost_savings", {})
    credit_savings = (credit_metrics or {}).get("cost_savings", {})

    total_savings = (fraud_savings.get("annual_savings", 0)
                     + credit_savings.get("annual_savings", 0))

    report = {
        "summary": {
            "fraud_annual_savings_usd":  fraud_savings.get("annual_savings", 0),
            "credit_annual_savings_usd": credit_savings.get("annual_savings", 0),
            "total_annual_savings_usd":  round(total_savings, 0),
            "fraud_roi_pct":             fraud_savings.get("roi_pct", 0),
            "credit_roi_pct":            credit_savings.get("roi_pct", 0),
        },
        "fraud_detail":  fraud_savings,
        "credit_detail": credit_savings,
        "model_performance": {
            "fraud_auc_roc":  (fraud_metrics or {}).get(
                "threshold_opt_f1", {}).get("auc_roc", None),
            "credit_auc_roc": (credit_metrics or {}).get(
                "threshold_opt_f1", {}).get("auc_roc", None),
            "fraud_gini":     (fraud_metrics or {}).get(
                "threshold_opt_f1", {}).get("gini", None),
            "credit_gini":    (credit_metrics or {}).get(
                "threshold_opt_f1", {}).get("gini", None),
        },
    }

    out_path = METRICS_DIR / "combined_impact_report.json"
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"[CostOptimizer] Combined report saved -> {out_path}")
    return report


# ── FP reduction analysis ─────────────────────────────────────────────────────

def false_positive_reduction_analysis(legacy_fp_rate: float,
                                       ml_fp_rate: float,
                                       annual_tx: int,
                                       cost_per_fp: float) -> dict:
    """Quantify analyst hours freed by reducing false positives."""
    legacy_fp = int(annual_tx * legacy_fp_rate)
    ml_fp     = int(annual_tx * ml_fp_rate)
    reduction = legacy_fp - ml_fp

    analyst_hours_freed  = reduction * 0.25     # ~15 min per alert
    analyst_cost_per_hr  = 80.0                 # USD
    annual_cost_freed    = analyst_hours_freed * analyst_cost_per_hr

    return {
        "legacy_fp_count":      legacy_fp,
        "ml_fp_count":          ml_fp,
        "fp_reduction":         reduction,
        "fp_reduction_pct":     round(reduction / (legacy_fp + 1e-9) * 100, 1),
        "analyst_hours_freed":  round(analyst_hours_freed, 0),
        "analyst_cost_freed":   round(annual_cost_freed, 0),
    }
