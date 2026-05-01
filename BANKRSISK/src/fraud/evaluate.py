"""
Fraud evaluation — config-driven.
Tous les coûts viennent de config/fraud.yaml (cost.*).
Logue le run dans le Model Registry.
"""
import json
import shap
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.config import METRICS_DIR, MODELS_DIR, get_fraud_config
from src.fraud.features import get_feature_matrix
from src.core.registry import ModelRegistry
from src.utils.metrics import (
    full_classification_report, find_optimal_threshold,
    cost_sensitive_threshold, pr_curve_df, roc_curve_df,
)
from src.utils.explainability import save_shap_artifacts


def _compute_cost_savings(metrics: dict, cfg: dict, fraud_rate: float) -> dict:
    c         = cfg["cost"]
    unit_fp   = c["unit_fp"]
    unit_fn   = c["unit_fn"]
    annual_tx = c["annual_volume"]
    fr        = c.get("fraud_rate") or fraud_rate

    annual_fraud = int(annual_tx * fr)
    annual_legit = annual_tx - annual_fraud

    # Legacy
    legacy_fp_n  = int(annual_legit * c["baseline_fp_rate"])
    legacy_fn_n  = int(annual_fraud  * (1 - c["baseline_recall"]))
    legacy_cost  = legacy_fp_n * unit_fp + legacy_fn_n * unit_fn

    # ML (extrapolé depuis le test set)
    m      = metrics["threshold_cost"]
    test_n = m["tp"] + m["fp"] + m["tn"] + m["fn"]
    scale  = annual_tx / test_n
    ml_fp  = int(m["fp"] * scale)
    ml_fn  = int(m["fn"] * scale)
    ml_cost = ml_fp * unit_fp + ml_fn * unit_fn
    savings = legacy_cost - ml_cost

    return {
        "annual_tx":           annual_tx,
        "annual_fraud":        annual_fraud,
        "legacy_fp_alerts":    legacy_fp_n,
        "legacy_fn_missed":    legacy_fn_n,
        "legacy_annual_cost":  round(legacy_cost, 0),
        "ml_fp_alerts":        ml_fp,
        "ml_fn_missed":        ml_fn,
        "ml_annual_cost":      round(ml_cost, 0),
        "annual_savings":      round(savings, 0),
        "roi_pct":             round(savings / max(legacy_cost, 1) * 100, 1),
        "unit_fp":             unit_fp,
        "unit_fn":             unit_fn,
    }


def run_evaluation(model, X_test: pd.DataFrame, y_test: pd.Series,
                   feature_names: list[str], model_path: Path,
                   dataset_info: dict, cfg: dict | None = None) -> dict:
    if cfg is None:
        cfg = get_fraud_config()

    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    Xf     = get_feature_matrix(X_test, cfg)
    y_prob = model.predict_proba(Xf)[:, 1]
    y_true = y_test.values

    # Métriques à 3 seuils
    m_05   = full_classification_report(y_true, y_prob, 0.5)
    opt_t  = find_optimal_threshold(y_true, y_prob, "f1")
    m_opt  = full_classification_report(y_true, y_prob, opt_t)
    cost_t, _ = cost_sensitive_threshold(
        y_true, y_prob,
        cost_fn=cfg["cost"]["unit_fn"],
        cost_fp=cfg["cost"]["unit_fp"],
    )
    m_cost = full_classification_report(y_true, y_prob, cost_t)

    metrics = {
        "threshold_0.5":    m_05,
        "threshold_opt_f1": m_opt,
        "threshold_cost":   m_cost,
    }

    # Coûts
    fraud_rate   = dataset_info.get("fraud_rate", cfg["cost"].get("fraud_rate") or 0.0017)
    cost_savings = _compute_cost_savings(metrics, cfg, fraud_rate)

    # Courbes
    pr_curve_df(y_true, y_prob).to_parquet(METRICS_DIR / "fraud_pr_curve.parquet",  index=False)
    roc_curve_df(y_true, y_prob).to_parquet(METRICS_DIR / "fraud_roc_curve.parquet", index=False)

    # SHAP
    shap_top = []
    try:
        inner = model
        for attr in ("named_steps", "steps"):
            if hasattr(inner, attr):
                steps = getattr(inner, attr)
                inner = (dict(steps) if not isinstance(steps, dict) else steps).get("clf", inner)
                break
        explainer = shap.TreeExplainer(inner)
        X_sample  = Xf.sample(min(800, len(Xf)), random_state=42)
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
        save_shap_artifacts(explainer, shap_vals, X_sample, MODELS_DIR / "shap", tag="fraud")
        print("  SHAP OK.")
    except Exception as e:
        print(f"  SHAP skipped: {e}")

    # Persist JSON (legacy — pour les pages détail)
    report = {**metrics, "cost_savings": cost_savings,
              "model_name": cfg["model"]["algorithm"],
              "shap_summary": {"top_features": shap_top}}
    with open(METRICS_DIR / "fraud_xgboost_smote_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Registry
    registry = ModelRegistry()
    registry.log_run(
        task           = "fraud",
        cfg            = cfg,
        dataset_info   = dataset_info,
        model_path     = str(model_path),
        metrics        = metrics,
        cost_savings   = cost_savings,
        feature_names  = feature_names,
        shap_top       = shap_top,
    )

    print(f"  AUC-ROC={m_opt['auc_roc']}  Gini={m_opt['gini']}  "
          f"Recall={m_opt['recall']:.2%}  Savings=${cost_savings['annual_savings']:,.0f}")
    return report
