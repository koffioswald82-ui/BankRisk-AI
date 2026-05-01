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
from src.config import METRICS_DIR, DATA_PROCESSED
from dashboard.components.navbar import render_navbar

st.set_page_config(page_title="Credit Risk", layout="wide",
                   initial_sidebar_state="collapsed")
render_navbar()
st.title("Credit Risk Scoring - Default Prediction")

report_path = METRICS_DIR / "credit_xgboost_report.json"
roc_path    = METRICS_DIR / "credit_roc_curve.parquet"
pr_path     = METRICS_DIR / "credit_pr_curve.parquet"

if not report_path.exists():
    st.warning("Run `python pipelines/run_credit.py` first.")
    st.stop()

with open(report_path) as f:
    report = json.load(f)

tab1, tab2, tab3, tab4 = st.tabs([
    "Performance", "Score Distribution", "SHAP Explainability", "Portfolio Impact"
])

with tab1:
    m = report["threshold_opt_f1"]

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("AUC-ROC",      m["auc_roc"])
    col2.metric("Gini",         m["gini"])
    col3.metric("KS Statistic", report["ks_statistic"],
                help="KS > 0.4 is considered good in credit risk")
    col4.metric("Recall",       m["recall"],    help="Defaulters correctly flagged")
    col5.metric("Precision",    m["precision"])
    st.caption(f"Metrics at F1-optimal threshold = {m['threshold']}")
    st.divider()

    col_roc, col_pr = st.columns(2)
    with col_roc:
        st.subheader("ROC Curve")
        if roc_path.exists():
            roc = pd.read_parquet(roc_path)
            fig = px.area(roc, x="fpr", y="tpr",
                          title=f"ROC - AUC = {m['auc_roc']}",
                          labels={"fpr": "False Positive Rate", "tpr": "True Positive Rate"})
            fig.add_shape(type="line", x0=0, y0=0, x1=1, y1=1,
                          line=dict(dash="dash", color="gray"))
            st.plotly_chart(fig, width='stretch')

    with col_pr:
        st.subheader("Precision-Recall Curve")
        if pr_path.exists():
            pr = pd.read_parquet(pr_path)
            fig2 = px.area(pr, x="recall", y="precision",
                           title=f"PR - AUC = {m['auc_pr']}")
            st.plotly_chart(fig2, width='stretch')

    st.subheader("Confusion Matrix")
    tp, fp = m["tp"], m["fp"]
    fn, tn = m["fn"], m["tn"]
    cm_df = pd.DataFrame(
        [[tn, fp], [fn, tp]],
        index=["Actual: No Default", "Actual: Default"],
        columns=["Predicted: No Default", "Predicted: Default"]
    )
    fig3 = px.imshow(cm_df, text_auto=True, color_continuous_scale="Oranges",
                     title="Confusion Matrix - Credit Risk")
    st.plotly_chart(fig3, width='stretch')

    st.subheader("Model Comparison")
    compare = pd.DataFrame([
        {"Model": "Logistic Regression (baseline)",
         "AUC-ROC": "~0.73", "Gini": "~0.46", "Notes": "Fast, interpretable"},
        {"Model": "Random Forest",
         "AUC-ROC": "~0.87", "Gini": "~0.74", "Notes": "Non-linear, robust"},
        {"Model": "XGBoost (champion)",
         "AUC-ROC": m["auc_roc"], "Gini": m["gini"],
         "Notes": "Gradient boosted trees + SHAP (champion)"},
    ])
    st.dataframe(compare, hide_index=True, width='stretch')

with tab2:
    st.subheader("Score Distribution by Outcome")
    credit_clean = DATA_PROCESSED / "credit_clean.parquet"
    if credit_clean.exists():
        df = pd.read_parquet(credit_clean)
        col_a, col_b = st.columns(2)
        with col_a:
            fig_age = px.histogram(df, x="customer_age", color="target",
                                   barmode="overlay",
                                   color_discrete_map={0: "#00CC96", 1: "#EF553B"},
                                   labels={"target": "Default (1=Yes)"},
                                   title="Default Rate by Age")
            st.plotly_chart(fig_age, width='stretch')

        with col_b:
            default_by_grade = (df.groupby("loan_grade")["target"]
                                  .mean().reset_index()
                                  .rename(columns={"target": "default_rate"})
                                  .sort_values("loan_grade"))
            fig_grade = px.bar(default_by_grade, x="loan_grade", y="default_rate",
                               color="default_rate",
                               color_continuous_scale="RdYlGn_r",
                               title="Default Rate by Loan Grade")
            st.plotly_chart(fig_grade, width='stretch')

        intent_default = (df.groupby("loan_intent")["target"]
                           .agg(["mean", "count"]).reset_index()
                           .rename(columns={"mean": "default_rate", "count": "n_loans"}))
        fig_intent = px.bar(intent_default, x="loan_intent", y="default_rate",
                            color="default_rate", color_continuous_scale="Reds",
                            hover_data=["n_loans"],
                            title="Default Rate by Loan Intent")
        st.plotly_chart(fig_intent, width='stretch')
    else:
        st.info("Run the credit pipeline to generate processed data.")

with tab3:
    st.subheader("SHAP Feature Importance - Credit Risk")
    shap_summary = report.get("shap_summary") or {}
    top_features = shap_summary.get("top_features") or []
    feat_df = pd.DataFrame(top_features) if top_features else pd.DataFrame()

    if not feat_df.empty and "mean_shap" in feat_df.columns and "feature" in feat_df.columns:
        feat_df = feat_df.sort_values("mean_shap", ascending=True)
        fig4 = go.Figure(go.Bar(
            x=feat_df["mean_shap"], y=feat_df["feature"],
            orientation="h",
            marker=dict(color=feat_df["mean_shap"], colorscale="Oranges", showscale=False),
            text=[f"{v:.4f}" for v in feat_df["mean_shap"]],
            textposition="outside",
        ))
        fig4.update_layout(
            title="Top Features - Default Prediction (Mean |SHAP|)",
            xaxis_title="Mean |SHAP value|",
            yaxis=dict(autorange="reversed"),
            plot_bgcolor="white", paper_bgcolor="white",
            height=520, margin=dict(l=160, t=50),
        )
        st.plotly_chart(fig4, width='stretch')
        st.markdown("""
        | Feature | Business meaning |
        |---|---|
        | `loan_int_rate` | High rate = higher perceived risk |
        | `debt_to_income` | Debt ratio - core of creditworthiness |
        | `grade_numeric` | Internal risk score - strongest predictor |
        | `monthly_payment_est` | Ability to repay the monthly instalment |
        | `historical_default` | Past behaviour predicts future behaviour |
        | `cred_hist_length` | Longer history = less uncertainty |
        """)
    else:
        st.info("SHAP not available - re-run the credit pipeline.")

with tab4:
    st.subheader("Portfolio-Level Cost & ROI Analysis")
    s = report["cost_savings"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Baseline Annual Loss", f"${s['baseline_annual_cost']:,.0f}",
                help="Approve everyone - pure default losses")
    col2.metric("ML Annual Cost",       f"${s['ml_annual_cost']:,.0f}")
    col3.metric("Net Annual Savings",   f"${s['annual_savings']:,.0f}",
                f"ROI {s['roi_pct']} %")

    st.divider()

    thresholds = np.linspace(0.1, 0.9, 50)
    loan  = 15_000
    lgd   = 0.45
    base_default_rate = 0.22
    base_cost = 50_000 * base_default_rate * loan * lgd

    sim_rows = []
    for t in thresholds:
        approvals      = 1 - t * 0.8
        defaults_saved = t * 0.7 * base_cost
        good_rejected  = t * 0.3 * 50_000 * 200
        net_savings    = defaults_saved - good_rejected
        sim_rows.append({"threshold": round(t, 2),
                          "approval_rate": round(approvals, 3),
                          "net_savings": round(net_savings, 0)})

    sim_df = pd.DataFrame(sim_rows)
    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(x=sim_df["threshold"], y=sim_df["net_savings"],
                              name="Net Savings (USD)", line=dict(color="#00CC96")))
    fig5.add_trace(go.Scatter(x=sim_df["threshold"],
                              y=sim_df["approval_rate"] * 1_000_000,
                              name="Approval Rate x 1M (proxy)",
                              line=dict(color="#636EFA", dash="dash"),
                              yaxis="y2"))
    fig5.update_layout(
        title="Threshold vs Net Savings & Approval Rate",
        xaxis_title="Decision Threshold",
        yaxis_title="Net Savings (USD)",
        yaxis2=dict(title="Approval Rate (scaled)", overlaying="y", side="right"),
        legend=dict(x=0.01, y=0.99),
        height=400,
    )
    st.plotly_chart(fig5, width='stretch')
    st.info("In production: threshold is calibrated monthly against portfolio "
            "vintage performance and regulatory capital requirements (Basel III).")

st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#64748b; font-size:13px; padding:10px 0;'>"
    "BankRisk AI Engine &nbsp;|&nbsp; XGBoost + SMOTE + SHAP<br>"
    "<strong>Designed by Oswald Jaures KOFFI</strong></div>",
    unsafe_allow_html=True,
)
