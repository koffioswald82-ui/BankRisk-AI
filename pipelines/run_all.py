"""
Pipeline complet — fraude + crédit + résumé exécutif.
Usage:
    python pipelines/run_all.py
    python pipelines/run_all.py --fraud-sample 50000
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipelines.run_fraud  import main as run_fraud
from pipelines.run_credit import main as run_credit
from src.core.registry import ModelRegistry


def main(fraud_sample: int | None = None) -> None:
    print("\n" + "█" * 58)
    print("  AI RISK & COST OPTIMIZATION ENGINE")
    print("█" * 58)

    run_fraud(sample=fraud_sample)
    run_credit()

    # Résumé depuis le registry (source de vérité unique)
    registry = ModelRegistry()
    summary  = registry.summary()

    print("\n" + "=" * 58)
    print("  RESUME EXECUTIF")
    print("=" * 58)

    total_savings = sum(
        v.get("annual_savings", 0) for v in summary.values()
        if v.get("annual_savings")
    )

    for task, info in summary.items():
        print(f"\n  [{info['module']}]")
        print(f"    AUC-ROC  : {info['auc_roc']}   Gini : {info['gini']}")
        print(f"    Économie : ${info['annual_savings']:>12,.0f} / an  "
              f"(ROI {info['roi_pct']} %)")

    print(f"\n  {'-'*40}")
    print(f"  TOTAL  : ${total_savings:>12,.0f} / an")
    print("=" * 58)
    print("\n  Dashboard : streamlit run dashboard/app.py\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fraud-sample", type=int, default=None)
    args = parser.parse_args()
    main(fraud_sample=args.fraud_sample)
