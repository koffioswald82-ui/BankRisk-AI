"""
Fraud Detection (AML) page.
Shows ROC curve, PR curve, confusion matrix, SHAP feature importance,
and threshold sensitivity analysis.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.config import METRICS_DIR, MODELS_DIR

st.set_page_config(page_title="Fraud Detection", layout="wide")
st.title("Fraud Detection - AML Transaction Monitoring")

# ── Load data ─────────────────────────────────────────────────────────────────
report_path  = METRICS_DIR / "fraud_xgboost_smote_report.json"
roc_path     = METRICS_DIR / "fraud_roc_curve.parquet"
pr_path      = METRICS_DIR / "fraud_pr_curve.parquet"

if not report_path.exists():
    st.warning("Run `python pipelines/run_fraud.py` first.")
    st.stop()

with open(report_path) as f:
    report = json.load(f)

# ── Metric selector ──────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["Performance", "Threshold Tuning",
                                    "SHAP Explainability", "Cost Analysis"])

with tab1:
    m_opt = report["threshold_opt_f1"]
    m_05  = report["threshold_0.5"]

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("AUC-ROC",    m_opt["auc_roc"])
    col2.metric("AUC-PR",     m_opt["auc_pr"])
    col3.metric("Gini",       m_opt["gini"])
    col4.metric("Recall",     m_opt["recall"],
                help="Fraud cases caught")
    col5.metric("Precision",  m_opt["precision"],
                help="Of flagged: truly fraud")

    st.caption(f"Metrics at F1-optimal threshold = {m_opt['threshold']}")
    st.divider()

    col_roc, col_pr = st.columns(2)

    with col_roc:
        st.subheader("ROC Curve")
        if roc_path.exists():
            roc = pd.read_parquet(roc_path)
            fig = px.area(roc, x="fpr", y="tpr",
                          labels={"fpr": "False Positive Rate",
                                  "tpr": "True Positive Rate"},
                          title=f"ROC - AUC = {m_opt['auc_roc']}")
            fig.add_shape(type="line", x0=0, y0=0, x1=1, y1=1,
                          line=dict(dash="dash", color="gray"))
            st.plotly_chart(fig, width='stretch')

    with col_pr:
        st.subheader("Precision-Recall Curve")
        if pr_path.exists():
            pr = pd.read_parquet(pr_path)
            fig2 = px.area(pr, x="recall", y="precision",
                           labels={"recall": "Recall",
                                   "precision": "Precision"},
                           title=f"PR - AUC = {m_opt['auc_pr']}")
            st.plotly_chart(fig2, width='stretch')

    # Confusion matrix
    st.subheader("Confusion Matrix (F1-optimal threshold)")
    tp, fp = m_opt["tp"], m_opt["fp"]
    fn, tn = m_opt["fn"], m_opt["tn"]
    cm_df = pd.DataFrame(
        [[tn, fp], [fn, tp]],
        index=["Actual: Legitimate", "Actual: Fraud"],
        columns=["Predicted: Legitimate", "Predicted: Fraud"]
    )
    fig3 = px.imshow(cm_df, text_auto=True, color_continuous_scale="Blues",
                     title="Confusion Matrix")
    st.plotly_chart(fig3, width='stretch')

    # Baseline vs ML comparison table
    st.subheader("Baseline vs ML Model")
    compare = pd.DataFrame([
        {"Model": "Legacy Rule Engine", "AUC-ROC": "~0.72",
         "Recall": "~0.85", "FP Rate": "~5.0%", "Annual Cost": "Legacy (reference)"},
        {"Model": "XGBoost + SMOTE",   "AUC-ROC": m_opt["auc_roc"],
         "Recall": m_opt["recall"],
         "FP Rate": f"~{round(fp/(fp+tn)*100, 2)}%",
         "Annual Cost": "Reduced"},
    ])
    st.dataframe(compare, hide_index=True, width='stretch')

with tab2:
    st.subheader("Threshold Sensitivity Analysis")
    st.info("Adjust the decision threshold to balance precision vs recall "
            "and observe the cost impact.")

    threshold_slider = st.slider("Decision Threshold", 0.01, 0.99, 0.5, 0.01)

    # Recompute metrics at selected threshold from stored values
    metrics_available = {
        "0.5":       report["threshold_0.5"],
        "F1-optimal": report["threshold_opt_f1"],
        "Cost-optimal": report["threshold_cost"],
    }
    rows = []
    for name, m in metrics_available.items():
        rows.append({
            "Threshold Label": name,
            "Threshold": m["threshold"],
            "Precision": m["precision"],
            "Recall":    m["recall"],
            "F1":        m["f1"],
            "TP": m["tp"], "FP": m["fp"],
            "FN": m["fn"], "TN": m["tn"],
        })
    st.dataframe(pd.DataFrame(rows), hide_index=True, width='stretch')

    st.markdown("""
    **Key trade-off:**
    - ↑ Threshold → fewer alerts, higher precision, lower recall (more fraud missed)
    - ↓ Threshold → more alerts, lower precision, higher recall (more manual review)
    """)

with tab3:
    st.subheader("SHAP Feature Importance")
    shap_summary = report.get("shap_summary") or {}
    top_features = shap_summary.get("top_features") or []
    feat_df = pd.DataFrame(top_features) if top_features else pd.DataFrame()

    if not feat_df.empty and "mean_shap" in feat_df.columns and "feature" in feat_df.columns:
        feat_df = feat_df.sort_values("mean_shap", ascending=True)
        fig4 = go.Figure(go.Bar(
            x=feat_df["mean_shap"], y=feat_df["feature"],
            orientation="h",
            marker=dict(color=feat_df["mean_shap"], colorscale="Reds", showscale=False),
            text=[f"{v:.4f}" for v in feat_df["mean_shap"]],
            textposition="outside",
        ))
        fig4.update_layout(
            title="Top Features — Mean |SHAP Value|",
            xaxis_title="Mean |SHAP|",
            yaxis=dict(autorange="reversed"),
            plot_bgcolor="white", paper_bgcolor="white",
            height=500, margin=dict(l=160, t=50),
        )
        st.plotly_chart(fig4, width='stretch')
        st.markdown("""
        **Interpretation :**
        - **V14, V12, V10** : Composantes PCA les plus discriminantes pour la fraude
        - **Amount_log** : Le montant de la transaction est un signal fort
        - **amount_hour_zscore** : Montants inhabituels a une heure donnee
        """)
    else:
        st.info("SHAP non disponible — relancez le pipeline pour les générer.")

with tab4:
    st.subheader("Annual Cost & Savings Analysis")
    s = report["cost_savings"]

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Legacy System Cost / Year", f"${s['legacy_annual_cost']:,.0f}")
    col_b.metric("ML System Cost / Year",     f"${s['ml_annual_cost']:,.0f}")
    col_c.metric("Annual Savings",             f"${s['annual_savings']:,.0f}",
                 f"ROI {s['roi_pct']} %")

    st.divider()
    col_d, col_e, col_f = st.columns(3)
    col_d.metric("Annual Transactions",        f"{s['annual_tx']:,}")
    col_e.metric("Estimated Annual Frauds",    f"{s['annual_fraud']:,}")
    col_f.metric("FP Alerts Eliminated",
                 f"{s['legacy_fp_alerts'] - s['ml_fp_alerts']:,}")

    # Waterfall chart
    categories = ["Legacy Cost", "FP Reduction Savings",
                  "FN Reduction Savings", "ML Cost"]
    values = [
        s["legacy_annual_cost"],
        -(s["legacy_fp_alerts"] - s["ml_fp_alerts"]) * 5,   # manual review $5/alert
        -(s["legacy_fn_missed"] - s["ml_fn_missed"]) * 250,  # $250 avg fraud
        s["ml_annual_cost"],
    ]
    fig5 = go.Figure(go.Waterfall(
        name="Cost Breakdown", orientation="v",
        measure=["absolute", "relative", "relative", "total"],
        x=categories, y=values,
        connector={"line": {"color": "rgb(63,63,63)"}},
        increasing={"marker": {"color": "#EF553B"}},
        decreasing={"marker": {"color": "#00CC96"}},
    ))
    fig5.update_layout(title="Cost Waterfall Analysis (Annual USD)", height=400)
    st.plotly_chart(fig5, width='stretch')

st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#64748b; font-size:13px; padding:10px 0;'>"
    "BankRisk AI Engine &nbsp;|&nbsp; XGBoost + SMOTE + SHAP<br>"
    "<strong>Realise par Oswald Jaures KOFFI</strong></div>",
    unsafe_allow_html=True,
)
