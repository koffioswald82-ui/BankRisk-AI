"""
Credit risk model training — piloté par config/credit.yaml.
"""
import joblib
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.config import MODELS_DIR, RANDOM_STATE, get_credit_config
from src.credit.features import get_feature_matrix

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb


def train(X_train: pd.DataFrame, X_test: pd.DataFrame,
          y_train: pd.Series, cfg: dict | None = None) -> tuple:
    if cfg is None:
        cfg = get_credit_config()

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    Xf_train, preprocessor = get_feature_matrix(X_train, cfg, fit=True)
    Xf_test,  _            = get_feature_matrix(X_test,  cfg,
                                                  preprocessor=preprocessor, fit=False)
    feature_names = list(Xf_train.columns)

    algo = cfg["model"]["algorithm"]
    pos_weight = (y_train == 0).sum() / max((y_train == 1).sum(), 1)
    print(f"  Algorithme : {algo}")

    if algo == "xgboost":
        p   = cfg["model"]["xgb"]
        clf = xgb.XGBClassifier(
            n_estimators      = p.get("n_estimators", 400),
            max_depth         = p.get("max_depth", 5),
            learning_rate     = p.get("learning_rate", 0.05),
            subsample         = p.get("subsample", 0.8),
            colsample_bytree  = p.get("colsample_bytree", 0.8),
            scale_pos_weight  = pos_weight,
            use_label_encoder = False,
            eval_metric       = "logloss",
            tree_method       = "hist",
            random_state      = cfg["model"].get("random_state", RANDOM_STATE),
        )
        clf.fit(Xf_train, y_train, eval_set=[(Xf_train, y_train)], verbose=False)

    elif algo == "random_forest":
        p   = cfg["model"]["rf"]
        clf = RandomForestClassifier(
            n_estimators = p.get("n_estimators", 300),
            max_depth    = p.get("max_depth", 12),
            class_weight = "balanced",
            n_jobs       = -1,
            random_state = cfg["model"].get("random_state", RANDOM_STATE),
        )
        clf.fit(Xf_train, y_train)

    elif algo == "logistic":
        clf = LogisticRegression(
            class_weight = "balanced",
            max_iter     = 1000,
            random_state = cfg["model"].get("random_state", RANDOM_STATE),
        )
        clf.fit(Xf_train, y_train)

    else:
        raise ValueError(f"Algorithme inconnu : {algo}")

    model_path = MODELS_DIR / "credit_champion.joblib"
    prep_path  = MODELS_DIR / "credit_preprocessor.joblib"
    joblib.dump(clf,          model_path)
    joblib.dump(preprocessor, prep_path)
    print(f"  Modele sauvegarde -> {model_path}")

    return clf, Xf_train, Xf_test, preprocessor, feature_names, model_path, prep_path


def load_champion() -> tuple:
    clf  = joblib.load(MODELS_DIR / "credit_champion.joblib")
    prep = joblib.load(MODELS_DIR / "credit_preprocessor.joblib")
    return clf, prep
