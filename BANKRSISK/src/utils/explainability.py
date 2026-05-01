"""SHAP-based model explainability utilities."""
import numpy as np
import pandas as pd
import shap
import joblib
from pathlib import Path


def compute_shap_values(model, X: pd.DataFrame,
                        model_type: str = "tree",
                        max_samples: int = 2000) -> tuple:
    """
    Compute SHAP values for a fitted model.

    Returns (explainer, shap_values, X_sample).
    """
    X_sample = X.sample(min(max_samples, len(X)), random_state=42)

    if model_type == "tree":
        explainer = shap.TreeExplainer(model)
    elif model_type == "linear":
        explainer = shap.LinearExplainer(model, X_sample)
    else:
        explainer = shap.KernelExplainer(model.predict_proba, X_sample.iloc[:100])

    shap_values = explainer(X_sample)
    return explainer, shap_values, X_sample


def top_features_by_shap(shap_values, feature_names: list, n: int = 15) -> pd.DataFrame:
    """Return DataFrame of features ranked by mean |SHAP| importance."""
    if hasattr(shap_values, "values"):
        vals = shap_values.values
    else:
        vals = shap_values

    # For binary classifiers TreeExplainer may return shape (n, f, 2)
    if vals.ndim == 3:
        vals = vals[:, :, 1]

    mean_abs = np.abs(vals).mean(axis=0)
    df = pd.DataFrame({
        "feature":    feature_names,
        "mean_shap":  mean_abs,
    }).sort_values("mean_shap", ascending=False).head(n).reset_index(drop=True)
    return df


def shap_summary_dict(shap_values, X_sample: pd.DataFrame, n: int = 15) -> dict:
    """Serialisable summary: top-N features + global mean absolute SHAP."""
    df = top_features_by_shap(shap_values, list(X_sample.columns), n=n)
    return {
        "top_features": df.to_dict(orient="records"),
        "global_mean_shap": float(np.abs(
            shap_values.values if hasattr(shap_values, "values") else shap_values
        ).mean()),
    }


def save_shap_artifacts(explainer, shap_values, X_sample: pd.DataFrame,
                        output_dir: Path, tag: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(explainer,   output_dir / f"{tag}_shap_explainer.joblib")
    joblib.dump(shap_values, output_dir / f"{tag}_shap_values.joblib")
    X_sample.to_parquet(output_dir / f"{tag}_shap_sample.parquet")


def load_shap_artifacts(output_dir: Path, tag: str):
    explainer   = joblib.load(output_dir / f"{tag}_shap_explainer.joblib")
    shap_values = joblib.load(output_dir / f"{tag}_shap_values.joblib")
    X_sample    = pd.read_parquet(output_dir / f"{tag}_shap_sample.parquet")
    return explainer, shap_values, X_sample
