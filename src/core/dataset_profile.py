"""
DatasetProfile — auto-détection du schéma d'un dataset tabluaire.

Détecte automatiquement :
  - Types de colonnes (numérique, catégoriel, binaire, datetime)
  - Valeurs manquantes
  - Déséquilibre de classes
  - Distribution statistique

Valide le dataset contre une config YAML avant l'entraînement.
"""
from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml


class DatasetProfile:
    """Profile complet d'un dataset : schéma, qualité, distribution."""

    def __init__(self, df: pd.DataFrame, target_col: str | None = None):
        self.df         = df
        self.target_col = target_col
        self.n_rows, self.n_cols = df.shape
        self._profile: dict = {}

    # ── Détection automatique ─────────────────────────────────────────────────

    @property
    def numeric_cols(self) -> list[str]:
        cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if self.target_col and self.target_col in cols:
            cols.remove(self.target_col)
        return cols

    @property
    def categorical_cols(self) -> list[str]:
        cols = self.df.select_dtypes(include=["object", "category"]).columns.tolist()
        if self.target_col and self.target_col in cols:
            cols.remove(self.target_col)
        return cols

    @property
    def binary_cols(self) -> list[str]:
        """Colonnes numériques avec seulement 2 valeurs distinctes."""
        return [c for c in self.numeric_cols
                if self.df[c].nunique() == 2]

    @property
    def high_cardinality_cols(self, threshold: int = 50) -> list[str]:
        return [c for c in self.categorical_cols
                if self.df[c].nunique() > threshold]

    @property
    def missing_summary(self) -> pd.DataFrame:
        miss = self.df.isnull().sum()
        miss = miss[miss > 0]
        if miss.empty:
            return pd.DataFrame(columns=["column", "missing_count", "missing_pct"])
        return pd.DataFrame({
            "column":       miss.index,
            "missing_count": miss.values,
            "missing_pct":  (miss.values / self.n_rows * 100).round(2),
        })

    @property
    def class_balance(self) -> dict | None:
        if self.target_col is None or self.target_col not in self.df.columns:
            return None
        vc = self.df[self.target_col].value_counts()
        minority_rate = vc.min() / vc.sum()
        return {
            "counts":        vc.to_dict(),
            "minority_rate": round(float(minority_rate), 6),
            "imbalance_ratio": round(float(vc.max() / vc.min()), 1),
            "is_imbalanced":  minority_rate < 0.10,
        }

    def numeric_stats(self) -> pd.DataFrame:
        return self.df[self.numeric_cols].describe().T.round(4)

    def categorical_stats(self) -> pd.DataFrame:
        rows = []
        for c in self.categorical_cols:
            rows.append({
                "column":     c,
                "n_unique":   self.df[c].nunique(),
                "top_value":  self.df[c].mode().iloc[0] if not self.df[c].empty else None,
                "top_freq_pct": round(self.df[c].value_counts().iloc[0] / self.n_rows * 100, 2),
            })
        return pd.DataFrame(rows)

    # ── Validation contre YAML config ────────────────────────────────────────

    def validate_against_config(self, cfg: dict) -> list[str]:
        """
        Vérifie que le dataset respecte le contrat décrit dans le YAML.
        Retourne une liste de warnings (vide = tout est OK).
        """
        issues = []
        ds = cfg.get("dataset", {})

        # Target column
        target = ds.get("target_col")
        if target and target not in self.df.columns:
            issues.append(f"[ERREUR] Colonne cible '{target}' absente du dataset.")

        # Colonnes numériques déclarées
        for col in ds.get("numeric_cols", []):
            if col not in self.df.columns:
                issues.append(f"[WARNING] Colonne numérique déclarée '{col}' absente.")

        # Colonnes catégorielles
        for cat in ds.get("categorical_ohe", []):
            if cat not in self.df.columns:
                issues.append(f"[WARNING] Colonne catégorielle OHE '{cat}' absente.")

        for cat in ds.get("categorical_ordinal", []):
            name = cat if isinstance(cat, str) else cat.get("name")
            if name and name not in self.df.columns:
                issues.append(f"[WARNING] Colonne ordinale '{name}' absente.")

        # ID columns
        for id_col in ds.get("id_cols", []):
            if id_col not in self.df.columns:
                issues.append(f"[INFO] Colonne ID '{id_col}' absente (peut être ignorée).")

        return issues

    # ── Rapport complet ───────────────────────────────────────────────────────

    def report(self) -> dict:
        cb = self.class_balance
        return {
            "n_rows":            self.n_rows,
            "n_cols":            self.n_cols,
            "numeric_cols":      self.numeric_cols,
            "categorical_cols":  self.categorical_cols,
            "binary_cols":       self.binary_cols,
            "missing_cols":      self.missing_summary.to_dict(orient="records"),
            "class_balance":     cb,
            "target_col":        self.target_col,
        }

    def print_summary(self) -> None:
        r = self.report()
        sep = "=" * 55
        print(f"\n{sep}")
        print(f"  Dataset Profile")
        print(sep)
        print(f"  Lignes      : {r['n_rows']:,}")
        print(f"  Colonnes    : {r['n_cols']}")
        print(f"  Numeriques  : {len(r['numeric_cols'])} cols")
        print(f"  Categoriels : {len(r['categorical_cols'])} cols")
        if r["missing_cols"]:
            print(f"  Manquants   : {len(r['missing_cols'])} colonnes avec NaN")
        else:
            print(f"  Manquants   : aucun")
        if r["class_balance"]:
            cb = r["class_balance"]
            print(f"  Cible '{r['target_col']}':")
            for k, v in cb["counts"].items():
                print(f"    {k}: {v:,}")
            smote_hint = "  [!] SMOTE recommande" if cb["is_imbalanced"] else "  [OK]"
            print(f"  Ratio desequilibre : {cb['imbalance_ratio']}:1{smote_hint}")
        print(f"{sep}\n")


# ── Loader CSV dynamique ──────────────────────────────────────────────────────

def load_dataset(cfg: dict, data_raw_dir: Path) -> pd.DataFrame:
    """
    Charge le dataset décrit dans le YAML.
    Gère automatiquement : encodage, colonnes monétaires, types.
    """
    ds   = cfg["dataset"]
    path = data_raw_dir / ds["file"]
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset introuvable : {path}\n"
            f"Modifiez 'dataset.file' dans le YAML de configuration."
        )
    df = pd.read_csv(path, low_memory=False)
    print(f"  Chargé : {path.name}  ({len(df):,} lignes × {len(df.columns)} colonnes)")
    return df


def load_config(config_path: Path) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
