"""
Pipeline fraude — lit config/fraud.yaml, entraîne, évalue, logue dans le registry.
Usage:
    python pipelines/run_fraud.py [--sample N]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import get_fraud_config
from src.fraud.preprocessing import run_preprocessing
from src.fraud.train import train
from src.fraud.evaluate import run_evaluation


def main(sample: int | None = None) -> dict:
    cfg = get_fraud_config()
    print(f"\n{'='*58}")
    print(f"  FRAUDE AML -- {cfg['labels']['module']}")
    print(f"  Dataset : {cfg['dataset']['file']}")
    print(f"  Algo    : {cfg['model']['algorithm']}")
    print(f"{'='*58}")

    X_train, X_test, y_train, y_test, profile = run_preprocessing(cfg)

    if sample:
        X_train = X_train.sample(min(sample, len(X_train)), random_state=42)
        y_train = y_train.loc[X_train.index]

    model, feature_names, model_path = train(X_train, y_train, cfg)

    report = run_evaluation(
        model, X_test, y_test,
        feature_names=feature_names,
        model_path=model_path,
        dataset_info=profile,
        cfg=cfg,
    )

    s = report["cost_savings"]
    print(f"\n  Economie : ${s['annual_savings']:,.0f} / an  (ROI {s['roi_pct']} %)")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=int, default=None)
    args = parser.parse_args()
    main(sample=args.sample)
