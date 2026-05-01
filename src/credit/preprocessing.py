"""
Credit risk preprocessing — piloté par config/credit.yaml.
Gère automatiquement : montants monétaires, colonnes binaires Y/N,
colonnes numériques, cible variable.
"""
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.config import DATA_RAW, DATA_PROCESSED, RANDOM_STATE, get_credit_config
from src.core.dataset_profile import DatasetProfile, load_dataset


def _clean_currency(series: pd.Series) -> pd.Series:
    return (series.astype(str)
                  .str.replace(r"[£$€,\s]", "", regex=True)
                  .str.strip()
                  .replace("nan", np.nan)
                  .astype(float))


def _encode_target(series: pd.Series, positive_class: str) -> pd.Series:
    return (series.astype(str).str.strip().str.upper()
            == str(positive_class).upper()).astype(int)


def _encode_binary(series: pd.Series, yes: str, no: str) -> pd.Series:
    mapping = {yes.upper(): 1, no.upper(): 0}
    return (series.astype(str).str.strip().str.upper()
                  .map(mapping).fillna(0).astype(int))


def clean(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    ds  = cfg["dataset"]
    df  = df.copy()

    # Dédoublonnage sur colonnes ID si présentes
    id_cols = [c for c in ds.get("id_cols", []) if c in df.columns]
    if id_cols:
        df = df.drop_duplicates(subset=id_cols)

    # Cible
    target      = ds["target_col"]
    pos_class   = ds["positive_class"]
    df["target"] = _encode_target(df[target], pos_class)
    df = df.dropna(subset=["target"]).reset_index(drop=True)

    # Colonnes monétaires (£, $, €)
    for col in ds.get("currency_cols", []):
        if col in df.columns:
            df[col] = _clean_currency(df[col])

    # Colonnes binaires Y/N
    for item in ds.get("binary_cols", []):
        col = item["name"] if isinstance(item, dict) else item
        yes = item.get("yes", "Y") if isinstance(item, dict) else "Y"
        no  = item.get("no",  "N") if isinstance(item, dict) else "N"
        if col in df.columns:
            df[col] = _encode_binary(df[col], yes, no)

    # Toutes les colonnes numériques → float
    for col in ds.get("numeric_cols", []):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Imputation : taux d'intérêt par grade, reste par médiane
    ord_cols = ds.get("categorical_ordinal", [])
    grade_col = None
    if ord_cols:
        first = ord_cols[0]
        grade_col = first["name"] if isinstance(first, dict) else first

    int_rate_col = next(
        (c for c in ds.get("numeric_cols", []) if "int_rate" in c or "rate" in c), None
    )
    if int_rate_col and int_rate_col in df.columns and grade_col and grade_col in df.columns:
        df[int_rate_col] = df.groupby(grade_col)[int_rate_col].transform(
            lambda x: x.fillna(x.median())
        )

    for col in ds.get("numeric_cols", []):
        if col in df.columns and df[col].isna().any():
            df[col] = df[col].fillna(df[col].median())

    # Cap outliers employment_duration @ p99
    emp_col = next(
        (c for c in ds.get("numeric_cols", []) if "employ" in c or "duration" in c), None
    )
    if emp_col and emp_col in df.columns:
        p99 = df[emp_col].quantile(0.99)
        df[emp_col] = df[emp_col].clip(upper=p99)

    return df.reset_index(drop=True)


def run_preprocessing(cfg: dict | None = None) -> tuple:
    if cfg is None:
        cfg = get_credit_config()

    df = load_dataset(cfg, DATA_RAW)

    profile = DatasetProfile(df, cfg["dataset"]["target_col"])
    issues  = profile.validate_against_config(cfg)
    for w in issues:
        print(f"  {w}")
    profile.print_summary()

    df = clean(df, cfg)

    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_parquet(DATA_PROCESSED / "credit_clean.parquet", index=False)

    drop_cols = (["target", cfg["dataset"]["target_col"]]
                 + [c for c in cfg["dataset"].get("id_cols", []) if c in df.columns])
    drop_cols = list(dict.fromkeys(drop_cols))  # unique, preserve order

    X = df.drop(columns=[c for c in drop_cols if c in df.columns])
    y = df["target"]

    test_size = cfg["model"].get("test_size", 0.20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size,
        random_state=cfg["model"].get("random_state", RANDOM_STATE),
        stratify=y,
    )

    default_rate = float(y.mean())
    profile_report = {**profile.report(), "fraud_rate": default_rate}

    print(f"  Train={len(X_train):,}  Test={len(X_test):,}  "
          f"Default rate={default_rate:.4%}")
    return X_train, X_test, y_train, y_test, profile_report
