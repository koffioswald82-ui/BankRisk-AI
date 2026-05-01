"""
Fraud preprocessing — entièrement piloté par config/fraud.yaml.
Fonctionne avec n'importe quel dataset de fraude binaire.
"""
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.config import DATA_RAW, DATA_PROCESSED, RANDOM_STATE, get_fraud_config
from src.core.dataset_profile import DatasetProfile, load_dataset


def _clean_target(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    ds  = cfg["dataset"]
    col = ds["target_col"]
    pos = ds["positive_class"]
    df  = df.copy()
    if df[col].dtype == object:
        df[col] = (df[col].str.strip().str.upper()
                   == str(pos).upper()).astype(int)
    else:
        df[col] = (df[col] == pos).astype(int)
    return df


def _scale_numeric(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    cols_to_scale = cfg["dataset"].get("numeric_cols_to_scale", [])
    cols_present  = [c for c in cols_to_scale if c in df.columns]
    if not cols_present:
        return df
    df = df.copy()
    scaler = RobustScaler()
    scaled = scaler.fit_transform(df[cols_present])
    for i, col in enumerate(cols_present):
        df[f"{col}_scaled"] = scaled[:, i]
    return df


def run_preprocessing(cfg: dict | None = None) -> tuple:
    if cfg is None:
        cfg = get_fraud_config()

    # 1. Charger
    df = load_dataset(cfg, DATA_RAW)

    # 2. Valider schéma
    target_col = cfg["dataset"]["target_col"]
    profile    = DatasetProfile(df, target_col)
    issues     = profile.validate_against_config(cfg)
    for w in issues:
        print(f"  {w}")
    profile.print_summary()

    # 3. Nettoyer
    df = df.drop_duplicates().reset_index(drop=True)
    df = _clean_target(df, cfg)
    df = df.dropna(subset=[target_col]).reset_index(drop=True)

    # 4. Scaler les colonnes brutes
    df = _scale_numeric(df, cfg)

    # 5. Sauvegarder
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_parquet(DATA_PROCESSED / "fraud_clean.parquet", index=False)

    # 6. Split
    X = df.drop(columns=[target_col])
    y = df[target_col]
    test_size = cfg["model"].get("test_size", 0.20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size,
        random_state=cfg["model"].get("random_state", RANDOM_STATE),
        stratify=y,
    )

    # Expose le profil pour le registry
    fraud_rate = float(y.mean())
    profile_report = {**profile.report(), "fraud_rate": fraud_rate}

    print(f"  Train={len(X_train):,}  Test={len(X_test):,}  "
          f"Fraud rate={fraud_rate:.4%}")
    return X_train, X_test, y_train, y_test, profile_report
