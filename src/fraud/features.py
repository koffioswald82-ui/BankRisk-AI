"""
Fraud feature engineering — config-driven.
Les features sont décrites dans config/fraud.yaml sous `features.engineered`.
Les colonnes PCA (préfixe configurable) sont gardées telles quelles.
"""
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.config import get_fraud_config


# ── Fonctions custom appelées depuis les expressions YAML ────────────────────

def _amount_zscore_by_hour(df: pd.DataFrame) -> pd.Series:
    """Zscore du montant dans chaque bucket horaire (proxy vélocité)."""
    bucket = (df["Time"] // 3_600).astype(int) if "Time" in df.columns else pd.Series(0, index=df.index)
    col    = "Amount" if "Amount" in df.columns else df.select_dtypes(include="number").columns[0]
    mu  = df.groupby(bucket)[col].transform("mean")
    std = df.groupby(bucket)[col].transform("std").fillna(1)
    return (df[col] - mu) / (std + 1e-9)


def _eval_expr(df: pd.DataFrame, name: str, expr: str) -> pd.Series:
    """Évalue une expression YAML sur le DataFrame."""
    if expr == "Amount_zscore_by_hour":
        return _amount_zscore_by_hour(df)
    # Contexte d'évaluation : colonnes + numpy
    ctx = {col: df[col] for col in df.columns}
    ctx["log1p"] = np.log1p
    ctx["sin"]   = np.sin
    ctx["cos"]   = np.cos
    try:
        return eval(expr, {"__builtins__": {}}, ctx)   # noqa: S307
    except Exception as e:
        raise ValueError(f"Erreur dans l'expression YAML '{name}': {expr}\n  → {e}")


def engineer(df: pd.DataFrame, cfg: dict | None = None) -> pd.DataFrame:
    """Applique les features engineered définies dans le YAML."""
    if cfg is None:
        cfg = get_fraud_config()

    df = df.copy()
    for feat in cfg.get("features", {}).get("engineered", []):
        name  = feat["name"]
        expr  = feat["expr"]
        cast  = feat.get("cast")
        serie = _eval_expr(df, name, expr)
        df[name] = serie.astype(int) if cast == "int" else serie

    return df


def get_feature_columns(df: pd.DataFrame, cfg: dict | None = None) -> list[str]:
    """Retourne la liste des colonnes features (sans la cible, sans Time/Amount bruts)."""
    if cfg is None:
        cfg = get_fraud_config()

    ds         = cfg["dataset"]
    target     = ds["target_col"]
    drop_raw   = ds.get("numeric_cols_to_scale", [])   # on garde les versions _scaled
    pca_prefix = ds.get("pca_prefix", "V")

    exclude = {target} | set(drop_raw) | set(ds.get("drop_cols", []))

    return [c for c in df.columns
            if c not in exclude
            and not c.endswith("_scaled") is False   # garde les *_scaled
            or c.startswith(pca_prefix)
            or c in [f["name"] for f in cfg.get("features", {}).get("engineered", [])]]


def get_feature_matrix(df: pd.DataFrame, cfg: dict | None = None) -> pd.DataFrame:
    """Pipeline complet : engineer → sélection des colonnes features."""
    if cfg is None:
        cfg = get_fraud_config()

    ds         = cfg["dataset"]
    target     = ds["target_col"]
    drop_raw   = set(ds.get("numeric_cols_to_scale", []))
    pca_prefix = ds.get("pca_prefix", "V")
    eng_names  = {f["name"] for f in cfg.get("features", {}).get("engineered", [])}
    id_cols    = set(ds.get("id_cols", []))

    df = engineer(df, cfg)

    keep = [
        c for c in df.columns
        if c != target
        and c not in id_cols
        and c not in drop_raw          # exclut Time, Amount bruts
        and (
            c.startswith(pca_prefix)   # V1…V28
            or c.endswith("_scaled")   # Time_scaled, Amount_scaled
            or c in eng_names          # features engineered
        )
    ]
    return df[keep]
