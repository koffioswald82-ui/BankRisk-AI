"""
Credit risk feature engineering — piloté par config/credit.yaml.
Les expressions engineered sont évaluées dynamiquement.
"""
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.config import get_credit_config


# ── Fonctions custom pour les expressions YAML ───────────────────────────────

def _annuity(loan_amnt: pd.Series, rate: pd.Series, term_years: pd.Series) -> pd.Series:
    r = rate / 100 / 12
    n = term_years * 12
    return np.where(
        r > 0,
        loan_amnt * r / (1 - (1 + r) ** (-n.clip(lower=1))),
        loan_amnt / n.clip(lower=1),
    )


def _grade_rank(series: pd.Series, order: list[str]) -> pd.Series:
    mapping = {g.upper(): i + 1 for i, g in enumerate(order)}
    mid = len(order) // 2 + 1
    return series.astype(str).str.upper().map(mapping).fillna(mid)


def engineer(df: pd.DataFrame, cfg: dict | None = None) -> pd.DataFrame:
    if cfg is None:
        cfg = get_credit_config()

    df      = df.copy()
    ds      = cfg["dataset"]

    # Récupère l'ordre des grades depuis la config ordinale
    grade_order = ["A", "B", "C", "D", "E", "F", "G"]
    for item in ds.get("categorical_ordinal", []):
        if isinstance(item, dict) and "order" in item:
            grade_order = item["order"]

    # Colonnes utiles pour les expressions
    amnt_col  = next((c for c in ds.get("numeric_cols", []) if "amnt" in c or "amount" in c), None)
    rate_col  = next((c for c in ds.get("numeric_cols", []) if "rate" in c), None)
    term_col  = next((c for c in ds.get("numeric_cols", []) if "term" in c), None)
    inc_col   = next((c for c in ds.get("numeric_cols", []) if "income" in c), None)
    emp_col   = next((c for c in ds.get("numeric_cols", []) if "employ" in c or "duration" in c), None)
    hist_col  = next((c for c in ds.get("numeric_cols", []) if "hist" in c), None)
    ord_cols  = ds.get("categorical_ordinal", [])
    grade_col = (ord_cols[0]["name"] if ord_cols and isinstance(ord_cols[0], dict)
                 else (ord_cols[0] if ord_cols else None))

    for feat in cfg.get("features", {}).get("engineered", []):
        name = feat["name"]
        expr = feat["expr"]
        try:
            if expr == "annuity(loan_amnt, loan_int_rate, term_years)":
                if amnt_col and rate_col and term_col:
                    df[name] = _annuity(df[amnt_col], df[rate_col], df[term_col])
            elif expr == "grade_rank(loan_grade)":
                if grade_col and grade_col in df.columns:
                    df[name] = _grade_rank(df[grade_col], grade_order)
            elif "clip(" in expr:
                # "customer_income / clip(employment_duration, 1)"
                if inc_col and emp_col:
                    df[name] = df[inc_col] / df[emp_col].clip(lower=1)
            elif "loan_amnt / (customer_income" in expr or "/ (customer_income" in expr:
                if amnt_col and inc_col:
                    df[name] = df[amnt_col] / (df[inc_col] + 1)
            elif "loan_amnt / clip(cred_hist" in expr or "cred_hist" in expr:
                if amnt_col and hist_col:
                    df[name] = df[amnt_col] / df[hist_col].clip(lower=1)
            else:
                # Évaluation générique
                ctx = {col: df[col] for col in df.columns}
                ctx.update({"log1p": np.log1p, "clip": np.clip})
                df[name] = eval(expr, {"__builtins__": {}}, ctx)  # noqa: S307
        except Exception as e:
            print(f"  [Feature '{name}'] skipped: {e}")

    return df


def build_preprocessor(cfg: dict) -> ColumnTransformer:
    ds          = cfg["dataset"]
    numeric     = ds.get("numeric_cols", [])
    eng_names   = [f["name"] for f in cfg.get("features", {}).get("engineered", [])]
    ohe_cols    = [c for c in ds.get("categorical_ohe", []) if isinstance(c, str)]
    ord_items   = ds.get("categorical_ordinal", [])
    ord_cols    = [i["name"] if isinstance(i, dict) else i for i in ord_items]
    ord_orders  = [i["order"] if isinstance(i, dict) and "order" in i else None
                   for i in ord_items]

    all_num = numeric + eng_names

    transformers = [
        ("num", Pipeline([("scaler", StandardScaler())]), all_num),
    ]
    if ohe_cols:
        transformers.append(
            ("ohe", Pipeline([("enc", OneHotEncoder(
                handle_unknown="ignore", sparse_output=False))]), ohe_cols)
        )
    if ord_cols:
        cats = [o if o else ["A","B","C","D","E","F","G"] for o in ord_orders]
        transformers.append(
            ("ord", Pipeline([("enc", OrdinalEncoder(
                categories=cats,
                handle_unknown="use_encoded_value",
                unknown_value=-1,
            ))]), ord_cols)
        )
    return ColumnTransformer(transformers=transformers, remainder="drop")


def get_feature_matrix(df: pd.DataFrame,
                        cfg: dict | None = None,
                        preprocessor: ColumnTransformer | None = None,
                        fit: bool = False) -> tuple[pd.DataFrame, ColumnTransformer]:
    if cfg is None:
        cfg = get_credit_config()

    df_eng = engineer(df, cfg)

    if preprocessor is None or fit:
        preprocessor = build_preprocessor(cfg)
        X_arr = preprocessor.fit_transform(df_eng)
    else:
        X_arr = preprocessor.transform(df_eng)

    # Reconstitue les noms de colonnes
    ds        = cfg["dataset"]
    numeric   = ds.get("numeric_cols", [])
    eng_names = [f["name"] for f in cfg.get("features", {}).get("engineered", [])]
    ohe_cols  = [c for c in ds.get("categorical_ohe", []) if isinstance(c, str)]

    ohe_names = []
    if ohe_cols and "ohe" in preprocessor.named_transformers_:
        ohe_names = (preprocessor.named_transformers_["ohe"]
                                  .named_steps["enc"]
                                  .get_feature_names_out(ohe_cols).tolist())

    ord_items = ds.get("categorical_ordinal", [])
    ord_names = [f"{(i['name'] if isinstance(i,dict) else i)}_ord" for i in ord_items]

    all_names = numeric + eng_names + ohe_names + ord_names
    # Ajuste si le nombre de colonnes ne correspond pas
    if len(all_names) != X_arr.shape[1]:
        all_names = [f"f_{i}" for i in range(X_arr.shape[1])]

    return pd.DataFrame(X_arr, columns=all_names, index=df.index), preprocessor
