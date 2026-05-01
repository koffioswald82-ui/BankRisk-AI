"""
Credit risk evaluation — config-driven.
Tous les coûts viennent de config/credit.yaml (cost.*).
Logue le run dans le Model Registry.
"""
import json
import shap
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import ks_2samp
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.config import METRICS_DIR, MODELS_DIR, get_credit_config
from src.core.registry import ModelRegistry
from src.utils.metrics import (
    full_classification_report, find_optimal_threshold,
    cost_sensitive_threshold, pr_curve_df, roc_curve_df,
)
from src.utils.explainability import save_shap_artifacts


def _ks(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    stat, _ = ks_2samp(y_prob[y_true == 1], y_prob[y_true == 0])
    return round(float(stat), 4)


def _compute_cost_savings(metrics: dict, cfg: dict, default_rate: float) -> dict:
    c        = cfg["cost"]
    loan     = c["avg_loan_amount"]
    lgd      = c["loss_given_default"]
    n_apps   = c.get("annual_applications", 50_000)
    dr       = c.get("baseline_default_rate") or default_rate

    baseline_defaults = int(n_apps * dr)
    baseline_cost     = baseline_defaults * loan * lgd

    m      = metrics["threshold_cost"]
    test_n = m["tp"] + m["fp"] + m["tn"] + m["fn"]
    scale  = n_apps / test_n

    ml_fn   = int(m["fn"] * scale)
    ml_fp   = int(m["fp"] * scale)
    ml_cost = (ml_fn * loan * lgd
               + ml_fp * c["cost_per_rejected_good"]
               + n_apps * c["underwriting_cost"] * 0.10)  # 90% automation
    savings = baseline_cost - ml_cost

    return {
        "annual_applications":       n_apps,
        "baseline_defaults":         baseline_defaults,
        "baseline_annual_cost":      round(baseline_cost, 0),
        "ml_fn_approved_defaulters": ml_fn,
        "ml_fp_rejected_good":       ml_fp,
        "ml_annual_cost":            round(ml_cost, 0),
        "annual_savings":            round(savings, 0),
        "roi_pct":                   round(savings / max(baseline_cost, 1) * 100, 1),
        "avg_loan_amount":           loan,
        "loss_given_default":        lgd,
    }


def run_evaluation(model, Xf_test: pd.DataFrame, y_test: pd.Series,
                   feature_names: list[str], model_path: Path,
                   preprocessor_path: Path, dataset_info: dict,
                   cfg: dict | None = None) -> dict:
    if cfg is None:
        cfg = get_credit_config()

    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    y_prob = model.predict_proba(Xf_test)[:, 1]
    y_true = y_test.values

    m_05   = full_classification_report(y_true, y_prob, 0.5)
    opt_t  = find_optimal_threshold(y_true, y_prob, "f1")
    m_opt  = full_classification_report(y_true, y_prob, opt_t)
    cost_fn = cfg["cost"]["avg_loan_amount"] * cfg["cost"]["loss_given_default"]
    cost_fp = cfg["cost"]["cost_per_rejected_good"]
    cost_t, _ = cost_sensitive_threshold(y_true, y_prob, cost_fn, cost_fp)
    m_cost = full_classification_report(y_true, y_prob, cost_t)

    metrics = {
        "ks_statistic":     _ks(y_true, y_prob),
        "threshold_0.5":    m_05,
        "threshold_opt_f1": m_opt,
        "threshold_cost":   m_cost,
    }

    default_rate = dataset_info.get("fraud_rate", 0.22)
    cost_savings = _compute_cost_savings(metrics, cfg, default_rate)

    # Courbes
    pr_curve_df(y_true, y_prob).to_parquet(METRICS_DIR / "credit_pr_curve.parquet",  index=False)
    roc_curve_df(y_true, y_prob).to_parquet(METRICS_DIR / "credit_roc_curve.parquet", index=False)

    # SHAP
    shap_top = []
    try:
        explainer = shap.TreeExplainer(model)
        X_sample  = Xf_test.sample(min(800, len(Xf_test)), random_state=42)
        shap_vals = explainer(X_sample)
        vals      = shap_vals.values
        if vals.ndim == 3:
            vals = vals[:, :, 1]
        mean_abs  = np.abs(vals).mean(axis=0)
        shap_top  = sorted(
            [{"feature": f, "mean_shap": round(v, 5)}
             for f, v in zip(list(X_sample.columns), mean_abs.tolist())],
            key=lambda x: x["mean_shap"], reverse=True,
        )[:15]
        save_shap_artifacts(explainer, shap_vals, X_sample, MODELS_DIR / "shap", tag="credit")
        print("  SHAP OK.")
    except Exception as e:
        print(f"  SHAP skipped: {e}")

    # Persist JSON legacy
    report = {**metrics, "cost_savings": cost_savings,
              "model_name": cfg["model"]["algorithm"],
              "shap_summary": {"top_features": shap_top}}
    with open(METRICS_DIR / "credit_xgboost_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Registry
    registry = ModelRegistry()
    registry.log_run(
        task               = "credit",
        cfg                = cfg,
        dataset_info       = dataset_info,
        model_path         = str(model_path),
        preprocessor_path  = str(preprocessor_path),
        metrics            = metrics,
        cost_savings       = cost_savings,
        feature_names      = feature_names,
        shap_top           = shap_top,
    )

    print(f"  AUC-ROC={m_opt['auc_roc']}  Gini={m_opt['gini']}  "
          f"KS={metrics['ks_statistic']}  Savings=${cost_savings['annual_savings']:,.0f}")
    return report
