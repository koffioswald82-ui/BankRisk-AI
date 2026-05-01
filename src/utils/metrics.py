"""Shared evaluation metrics — AUC, PR-curve, cost-based, Gini."""
import numpy as np
import pandas as pd
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    precision_recall_curve,
    roc_curve,
    classification_report,
    confusion_matrix,
)


def full_classification_report(y_true: np.ndarray, y_prob: np.ndarray,
                                threshold: float = 0.5) -> dict:
    """Return a comprehensive dict of metrics for a binary classifier."""
    y_pred = (y_prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    auc_roc = roc_auc_score(y_true, y_prob)
    auc_pr  = average_precision_score(y_true, y_prob)
    gini    = 2 * auc_roc - 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1        = (2 * precision * recall / (precision + recall)
                 if (precision + recall) > 0 else 0.0)
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0

    return {
        "auc_roc":    round(auc_roc, 4),
        "auc_pr":     round(auc_pr, 4),
        "gini":       round(gini, 4),
        "precision":  round(precision, 4),
        "recall":     round(recall, 4),
        "f1":         round(f1, 4),
        "specificity":round(specificity, 4),
        "tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn),
        "threshold":  threshold,
    }


def find_optimal_threshold(y_true: np.ndarray, y_prob: np.ndarray,
                            metric: str = "f1") -> float:
    """Find the probability threshold maximising a given metric."""
    thresholds = np.linspace(0.01, 0.99, 200)
    best_val, best_t = -np.inf, 0.5

    for t in thresholds:
        y_pred = (y_prob >= t).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

        if metric == "f1":
            prec = tp / (tp + fp + 1e-9)
            rec  = tp / (tp + fn + 1e-9)
            val  = 2 * prec * rec / (prec + rec + 1e-9)
        elif metric == "recall_at_90_precision":
            prec = tp / (tp + fp + 1e-9)
            val  = tp / (tp + fn + 1e-9) if prec >= 0.90 else 0.0
        else:
            raise ValueError(f"Unknown metric: {metric}")

        if val > best_val:
            best_val, best_t = val, t

    return round(best_t, 4)


def cost_sensitive_threshold(y_true: np.ndarray, y_prob: np.ndarray,
                              cost_fn: float, cost_fp: float) -> tuple[float, float]:
    """
    Minimise expected cost = FN_count * cost_fn + FP_count * cost_fp.
    Returns (optimal_threshold, min_expected_cost).
    """
    thresholds = np.linspace(0.01, 0.99, 500)
    best_cost, best_t = np.inf, 0.5

    for t in thresholds:
        y_pred = (y_prob >= t).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        cost = fn * cost_fn + fp * cost_fp
        if cost < best_cost:
            best_cost, best_t = cost, t

    return round(best_t, 4), round(best_cost, 2)


def pr_curve_df(y_true: np.ndarray, y_prob: np.ndarray) -> pd.DataFrame:
    precision, recall, thresholds = precision_recall_curve(y_true, y_prob)
    return pd.DataFrame({
        "precision": precision[:-1],
        "recall":    recall[:-1],
        "threshold": thresholds,
    })


def roc_curve_df(y_true: np.ndarray, y_prob: np.ndarray) -> pd.DataFrame:
    fpr, tpr, thresholds = roc_curve(y_true, y_prob)
    return pd.DataFrame({"fpr": fpr, "tpr": tpr, "threshold": thresholds})
