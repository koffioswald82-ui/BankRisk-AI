"""
Model Registry — persiste l'historique de chaque run d'entraînement.

Le dashboard lit UNIQUEMENT ce fichier pour afficher les résultats.
Structure : models/registry.json
  {
    "fraud":  { last_run: {...}, history: [{...}, ...] },
    "credit": { last_run: {...}, history: [{...}, ...] }
  }

Chaque run contient :
  - timestamp, config_hash
  - dataset_info (n_rows, target, imbalance_ratio, ...)
  - model_path, preprocessor_path
  - metrics (auc_roc, gini, f1, ks, ...)
  - cost_savings (avant/après complets)
  - feature_names, shap_top_features
  - thresholds dict (0.5, opt_f1, cost)
  - labels (depuis le YAML, pour le dashboard)
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REGISTRY_PATH_DEFAULT = Path(__file__).resolve().parents[2] / "models" / "registry.json"


class ModelRegistry:
    def __init__(self, path: Path = REGISTRY_PATH_DEFAULT):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._data = self._load()

    # ── I/O ──────────────────────────────────────────────────────────────────

    def _load(self) -> dict:
        if self.path.exists():
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, default=str)

    # ── Écriture d'un run ─────────────────────────────────────────────────────

    def log_run(
        self,
        task: str,               # "fraud" ou "credit"
        cfg: dict,               # config YAML complet
        dataset_info: dict,      # depuis DatasetProfile.report()
        model_path: str,
        metrics: dict,           # depuis evaluate.py
        cost_savings: dict,
        feature_names: list[str],
        shap_top: list[dict] | None = None,
        preprocessor_path: str | None = None,
    ) -> None:

        run = {
            "timestamp":        datetime.now(timezone.utc).isoformat(),
            "config_hash":      _hash_config(cfg),
            "config_labels":    cfg.get("labels", {}),
            "config_cost":      cfg.get("cost", {}),
            "dataset_info":     dataset_info,
            "model_path":       str(model_path),
            "preprocessor_path": str(preprocessor_path) if preprocessor_path else None,
            "feature_names":    feature_names,
            "shap_top_features": shap_top or [],
            "metrics":          metrics,          # contient threshold_0.5, opt_f1, cost
            "cost_savings":     cost_savings,
        }

        if task not in self._data:
            self._data[task] = {"last_run": None, "history": []}

        self._data[task]["last_run"] = run
        self._data[task]["history"].append({
            "timestamp":    run["timestamp"],
            "auc_roc":      metrics.get("threshold_opt_f1", {}).get("auc_roc"),
            "gini":         metrics.get("threshold_opt_f1", {}).get("gini"),
            "annual_savings": cost_savings.get("annual_savings"),
        })
        # Garde les 20 derniers runs
        self._data[task]["history"] = self._data[task]["history"][-20:]

        self._save()
        print(f"[Registry] Run '{task}' enregistre -> {self.path}")

    # ── Lecture ───────────────────────────────────────────────────────────────

    def get_last_run(self, task: str) -> dict | None:
        return self._data.get(task, {}).get("last_run")

    def get_history(self, task: str) -> list[dict]:
        return self._data.get(task, {}).get("history", [])

    def get_all_tasks(self) -> list[str]:
        return list(self._data.keys())

    def is_trained(self, task: str) -> bool:
        run = self.get_last_run(task)
        if not run:
            return False
        return Path(run["model_path"]).exists()

    def summary(self) -> dict:
        """Résumé exécutif — utilisé par le dashboard."""
        result = {}
        for task in self._data:
            run = self._data[task].get("last_run")
            if not run:
                continue
            m   = run["metrics"].get("threshold_opt_f1", {})
            s   = run["cost_savings"]
            lbl = run.get("config_labels", {})
            result[task] = {
                "module":           lbl.get("module", task),
                "timestamp":        run["timestamp"],
                "dataset_rows":     run["dataset_info"].get("n_rows"),
                "fraud_rate":       run["dataset_info"].get("fraud_rate"),
                "auc_roc":          m.get("auc_roc"),
                "gini":             m.get("gini"),
                "f1":               m.get("f1"),
                "recall":           m.get("recall"),
                "precision":        m.get("precision"),
                "ks_statistic":     run["metrics"].get("ks_statistic"),
                "threshold_opt":    m.get("threshold"),
                "annual_savings":   s.get("annual_savings"),
                "legacy_cost":      s.get("legacy_annual_cost") or s.get("baseline_annual_cost"),
                "ml_cost":          s.get("ml_annual_cost"),
                "roi_pct":          s.get("roi_pct"),
                "fp_legacy":        s.get("legacy_fp_alerts") or s.get("baseline_defaults"),
                "fp_ml":            s.get("ml_fp_alerts")     or s.get("ml_fn_approved_defaulters"),
                "fn_legacy":        s.get("legacy_fn_missed")  or s.get("baseline_defaults"),
                "fn_ml":            s.get("ml_fn_missed")      or s.get("ml_fn_approved_defaulters"),
                "cost_cfg":         run.get("config_cost", {}),
                "labels":           lbl,
                "shap_top":         run.get("shap_top_features", []),
                "history":          self.get_history(task),
            }
        return result


# ── Helper ────────────────────────────────────────────────────────────────────

def _hash_config(cfg: dict) -> str:
    def _normalize(obj):
        if isinstance(obj, dict):
            return {str(k): _normalize(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_normalize(i) for i in obj]
        return obj
    raw = json.dumps(_normalize(cfg), sort_keys=True, default=str).encode()
    return hashlib.md5(raw).hexdigest()[:8]
