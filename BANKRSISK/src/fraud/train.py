"""
Fraud model training — piloté par config/fraud.yaml.
Sélectionne automatiquement l'algorithme décrit dans model.algorithm.
"""
import joblib
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.config import MODELS_DIR, RANDOM_STATE, get_fraud_config
from src.fraud.features import get_feature_matrix

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import xgboost as xgb


def _build_xgb(cfg: dict, y_train: pd.Series) -> xgb.XGBClassifier:
    p   = cfg["model"]["xgb"]
    pos_weight = (y_train == 0).sum() / max((y_train == 1).sum(), 1)
    return xgb.XGBClassifier(
        n_estimators      = p.get("n_estimators", 500),
        max_depth         = p.get("max_depth", 6),
        learning_rate     = p.get("learning_rate", 0.05),
        subsample         = p.get("subsample", 0.8),
        colsample_bytree  = p.get("colsample_bytree", 0.8),
        scale_pos_weight  = pos_weight,
        use_label_encoder = False,
        eval_metric       = "aucpr",
        tree_method       = "hist",
        random_state      = cfg["model"].get("random_state", RANDOM_STATE),
    )


def _build_rf(cfg: dict) -> RandomForestClassifier:
    p = cfg["model"]["rf"]
    return RandomForestClassifier(
        n_estimators  = p.get("n_estimators", 200),
        max_depth     = p.get("max_depth", 10),
        class_weight  = "balanced",
        n_jobs        = -1,
        random_state  = cfg["model"].get("random_state", RANDOM_STATE),
    )


def _build_lr(cfg: dict) -> Pipeline:
    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf",    LogisticRegression(
            class_weight = "balanced",
            max_iter     = 1000,
            C            = 0.1,
            random_state = cfg["model"].get("random_state", RANDOM_STATE),
        )),
    ])


def train(X_train: pd.DataFrame, y_train: pd.Series,
          cfg: dict | None = None) -> tuple:
    """
    Entraîne le modèle décrit dans le YAML.
    Retourne (model, feature_names, model_path).
    """
    if cfg is None:
        cfg = get_fraud_config()

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    Xf = get_feature_matrix(X_train, cfg)
    feature_names = list(Xf.columns)

    algo = cfg["model"]["algorithm"]
    print(f"  Algorithme : {algo}")

    if algo == "xgboost_smote":
        strategy = cfg["model"].get("smote_strategy", 0.1)
        model = ImbPipeline([
            ("smote", SMOTE(sampling_strategy=strategy,
                            random_state=cfg["model"].get("random_state", RANDOM_STATE))),
            ("clf",   _build_xgb(cfg, y_train)),
        ])
    elif algo == "xgboost":
        model = _build_xgb(cfg, y_train)
    elif algo == "random_forest":
        model = _build_rf(cfg)
    elif algo == "logistic":
        model = _build_lr(cfg)
    else:
        raise ValueError(f"Algorithme inconnu : {algo}. "
                         f"Options : logistic, random_forest, xgboost, xgboost_smote")

    model.fit(Xf, y_train)

    model_path = MODELS_DIR / "fraud_champion.joblib"
    joblib.dump(model, model_path)
    print(f"  Modele sauvegarde -> {model_path}")

    return model, feature_names, model_path


def load_champion():
    return joblib.load(MODELS_DIR / "fraud_champion.joblib")
