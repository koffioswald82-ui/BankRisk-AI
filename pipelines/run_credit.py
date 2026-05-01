"""
Pipeline crédit — lit config/credit.yaml, entraîne, évalue, logue dans le registry.
Usage:
    python pipelines/run_credit.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import get_credit_config
from src.credit.preprocessing import run_preprocessing
from src.credit.train import train
from src.credit.evaluate import run_evaluation


def main() -> dict:
    cfg = get_credit_config()
    print(f"\n{'='*58}")
    print(f"  RISQUE CREDIT -- {cfg['labels']['module']}")
    print(f"  Dataset : {cfg['dataset']['file']}")
    print(f"  Algo    : {cfg['model']['algorithm']}")
    print(f"{'='*58}")

    X_train, X_test, y_train, y_test, profile = run_preprocessing(cfg)

    model, Xf_train, Xf_test, preprocessor, feature_names, model_path, prep_path = \
        train(X_train, X_test, y_train, cfg)

    report = run_evaluation(
        model, Xf_test, y_test,
        feature_names=feature_names,
        model_path=model_path,
        preprocessor_path=prep_path,
        dataset_info=profile,
        cfg=cfg,
    )

    s = report["cost_savings"]
    print(f"\n  Economie : ${s['annual_savings']:,.0f} / an  (ROI {s['roi_pct']} %)")
    return report


if __name__ == "__main__":
    main()
