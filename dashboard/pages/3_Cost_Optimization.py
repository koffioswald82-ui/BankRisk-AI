import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.config import get_fraud_config, get_credit_config
from src.core.registry import ModelRegistry
from dashboard.components.navbar import render_navbar

st.set_page_config(page_title="Cost Simulator", layout="wide",
                   initial_sidebar_state="collapsed")
render_navbar()
st.title("Cost Simulator - Business Optimization")

registry = ModelRegistry()
summary  = registry.summary()
fc       = get_fraud_config()
cc       = get_credit_config()

fraud_cost  = fc.get("cost", {})
credit_cost = cc.get("cost", {})
fraud_info  = summary.get("fraud",  {})
credit_info = summary.get("credit", {})

# ── Fraud simulator ───────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Fraud AML Simulator")
st.caption("All parameters are initialised from `config/fraud.yaml` - adjust freely.")

col_p, col_r = st.columns([1, 2])

with col_p:
    sim_vol   = st.number_input(
        "Annual transaction volume",
        value=int(fraud_cost.get("annual_volume", 10_000_000)),
        step=1_000_000, format="%d", key="f_vol")
    sim_ufp   = st.number_input(
        f"Cost / false alert ($) - {fc['labels']['unit_fp_label']}",
        value=float(fraud_cost.get("unit_fp", 5)), step=1.0, key="f_ufp")
    sim_ufn   = st.number_input(
        f"Loss / missed fraud ($) - {fc['labels']['unit_fn_label']}",
        value=float(fraud_cost.get("unit_fn", 250)), step=10.0, key="f_ufn")
    sim_fp_rt = st.slider("ML FP Rate (%)", 0.1, 5.0,
                           float(fraud_cost.get("unit_fp", 5) / 100), 0.1, key="f_fpr") / 100
    sim_rec   = st.slider("ML Recall (%)", 50, 99,
                           int((fraud_info.get("recall") or 0.90) * 100), 1, key="f_rec") / 100
    fr        = fraud_info.get("fraud_rate") or fraud_cost.get("fraud_rate") or 0.0017
    bp        = float(fraud_cost.get("baseline_fp_rate", 0.05))
    br        = float(fraud_cost.get("baseline_recall",  0.85))

with col_r:
    leg_fp = int(sim_vol * (1 - fr) * bp)
    leg_fn = int(sim_vol * fr * (1 - br))
    leg_c  = leg_fp * sim_ufp + leg_fn * sim_ufn
    ml_fp  = int(sim_vol * (1 - fr) * sim_fp_rt)
    ml_fn  = int(sim_vol * fr * (1 - sim_rec))
    ml_c   = ml_fp * sim_ufp + ml_fn * sim_ufn
    sav    = leg_c - ml_c
    roi    = sav / max(leg_c, 1) * 100

    fp_red       = leg_fp - ml_fp
    analyst_hrs  = fp_red * 0.25
    analyst_cost = analyst_hrs * 80

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Legacy cost / year",      f"${leg_c:,.0f}")
    m2.metric("ML cost / year",          f"${ml_c:,.0f}", f"-${leg_c-ml_c:,.0f}")
    m3.metric("Savings / year",          f"${sav:,.0f}",  f"ROI {roi:.1f} %")
    m4.metric("Analyst hours freed",     f"{analyst_hrs:,.0f} h", f"${analyst_cost:,.0f}")

    cats = [fc["labels"]["unit_fp_label"], fc["labels"]["unit_fn_label"], "Total"]
    fig  = go.Figure()
    fig.add_trace(go.Bar(name="Legacy", x=cats,
                          y=[leg_fp*sim_ufp, leg_fn*sim_ufn, leg_c],
                          marker_color="#ef4444",
                          text=[f"${v:,.0f}" for v in [leg_fp*sim_ufp, leg_fn*sim_ufn, leg_c]],
                          textposition="outside"))
    fig.add_trace(go.Bar(name="ML", x=cats,
                          y=[ml_fp*sim_ufp, ml_fn*sim_ufn, ml_c],
                          marker_color="#22c55e",
                          text=[f"${v:,.0f}" for v in [ml_fp*sim_ufp, ml_fn*sim_ufn, ml_c]],
                          textposition="outside"))
    fig.update_layout(barmode="group", height=320,
                       plot_bgcolor="white", paper_bgcolor="white",
                       yaxis_title="USD / year", yaxis=dict(gridcolor="#f1f5f9"),
                       legend=dict(orientation="h", y=-0.28),
                       margin=dict(t=20, b=60))
    st.plotly_chart(fig, width='stretch')
    st.info(
        f"**False alert reduction**: {fp_red:,} alerts eliminated "
        f"({round(fp_red/max(leg_fp,1)*100,1)} %) - "
        f"**{analyst_hrs:,.0f} analyst hours freed** - "
        f"**Value: ${analyst_cost:,.0f} / year**"
    )

# ── Credit risk simulator ─────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Credit Risk Simulator")
st.caption("Parameters initialised from `config/credit.yaml`.")

col_cp, col_cr = st.columns([1, 2])

with col_cp:
    sim_apps = st.number_input(
        "Applications / year",
        value=int(credit_cost.get("annual_applications", 50_000)),
        step=5_000, format="%d", key="c_apps")
    sim_loan = st.number_input(
        "Average loan amount ($)",
        value=float(credit_cost.get("avg_loan_amount", 15_000)),
        step=1_000.0, key="c_loan")
    sim_lgd  = st.slider(
        "Loss Given Default - LGD (%)", 20, 70,
        int(credit_cost.get("loss_given_default", 0.45) * 100), 5, key="c_lgd") / 100
    sim_dr   = st.slider(
        "Portfolio default rate (%)", 5, 40,
        int((credit_info.get("fraud_rate") or credit_cost.get("baseline_default_rate") or 0.22) * 100),
        1, key="c_dr") / 100
    sim_crec = st.slider(
        "ML Recall - defaults detected (%)", 50, 95,
        int((credit_info.get("recall") or 0.80) * 100), 1, key="c_rec") / 100
    sim_opp  = st.number_input(
        "Opportunity cost per rejected good file ($)",
        value=float(credit_cost.get("cost_per_rejected_good", 200)),
        step=10.0, key="c_opp")

with col_cr:
    n_def     = int(sim_apps * sim_dr)
    base_loss = n_def * sim_loan * sim_lgd
    ml_fn_c   = int(n_def * (1 - sim_crec))
    ml_fp_c   = int((sim_apps - n_def) * 0.05)
    ml_loss   = ml_fn_c * sim_loan * sim_lgd + ml_fp_c * sim_opp
    sav_c     = base_loss - ml_loss
    roi_c     = sav_c / max(base_loss, 1) * 100

    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("Baseline loss / year", f"${base_loss:,.0f}",
               help=f"{n_def:,} defaults x ${sim_loan:,} x {sim_lgd:.0%} LGD")
    mc2.metric("ML cost / year",       f"${ml_loss:,.0f}",  f"-${base_loss-ml_loss:,.0f}")
    mc3.metric("Savings / year",       f"${sav_c:,.0f}",    f"ROI {roi_c:.1f} %")

    fig_wf = go.Figure(go.Waterfall(
        orientation="v",
        measure=["absolute", "relative", "relative", "total"],
        x=["Baseline losses",
           f"Defaults avoided\n({n_def - ml_fn_c:,})",
           f"Good files\nrejected ({ml_fp_c:,})",
           "Residual ML cost"],
        y=[base_loss,
           -(base_loss - ml_fn_c * sim_loan * sim_lgd),
           ml_fp_c * sim_opp,
           0],
        text=[f"${base_loss:,.0f}",
              f"-${base_loss - ml_fn_c*sim_loan*sim_lgd:,.0f}",
              f"+${ml_fp_c*sim_opp:,.0f}",
              f"${ml_loss:,.0f}"],
        textposition="outside",
        connector={"line": {"color": "#94a3b8"}},
        decreasing={"marker": {"color": "#22c55e"}},
        increasing={"marker": {"color": "#ef4444"}},
        totals={"marker": {"color": "#3b82f6"}},
    ))
    fig_wf.update_layout(
        title=f"Credit Waterfall - {sim_apps:,} applications | LGD {sim_lgd:.0%}",
        height=340, plot_bgcolor="white", paper_bgcolor="white",
        yaxis_title="USD", yaxis=dict(gridcolor="#f1f5f9"),
        margin=dict(t=50, b=10))
    st.plotly_chart(fig_wf, width='stretch')

# ── ROI sensitivity ───────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("ROI Sensitivity to Decision Threshold")

thresholds = np.linspace(0.05, 0.95, 80)
rows_fraud, rows_credit = [], []

for t in thresholds:
    rec_t  = min(0.99, sim_rec * (1 - (t - 0.5).clip(0) * 0.8))
    fpr_t  = max(0.001, sim_fp_rt * (1 - t * 0.6))
    fp_t   = int(sim_vol * (1-fr) * fpr_t)
    fn_t   = int(sim_vol * fr * (1 - rec_t))
    cost_t = fp_t * sim_ufp + fn_t * sim_ufn
    rows_fraud.append({"threshold": round(t,3),
                        "roi": round((leg_c-cost_t)/max(leg_c,1)*100,1)})

    rec_ct  = min(0.95, sim_crec * (1 - (t - 0.5).clip(0) * 0.6))
    fpr_ct  = max(0.01, 0.05 * (1 - t * 0.5))
    fn_ct   = int(n_def * (1 - rec_ct))
    fp_ct   = int((sim_apps - n_def) * fpr_ct)
    cost_ct = fn_ct * sim_loan * sim_lgd + fp_ct * sim_opp
    rows_credit.append({"threshold": round(t,3),
                         "roi": round((base_loss-cost_ct)/max(base_loss,1)*100,1)})

df_f_sens = pd.DataFrame(rows_fraud)
df_c_sens = pd.DataFrame(rows_credit)

fig_sens = go.Figure()
fig_sens.add_trace(go.Scatter(x=df_f_sens["threshold"], y=df_f_sens["roi"],
                               name="Fraud ROI (%)", line=dict(color="#3b82f6", width=2.5)))
fig_sens.add_trace(go.Scatter(x=df_c_sens["threshold"], y=df_c_sens["roi"],
                               name="Credit ROI (%)", line=dict(color="#f59e0b", width=2.5)))

for task, info, color in [("fraud",  fraud_info,  "#3b82f6"),
                           ("credit", credit_info, "#f59e0b")]:
    opt_t = info.get("threshold_opt")
    if opt_t:
        fig_sens.add_vline(x=float(opt_t), line_dash="dash", line_color=color, opacity=0.6,
                            annotation_text=f"Optimal threshold {task} ({opt_t})",
                            annotation_position="top right")

fig_sens.update_layout(
    title="ROI (%) as a function of the decision threshold",
    xaxis_title="Decision threshold",
    yaxis_title="ROI (%)",
    plot_bgcolor="white", paper_bgcolor="white",
    yaxis=dict(gridcolor="#f1f5f9"),
    legend=dict(orientation="h", y=-0.18),
    height=380,
)
st.plotly_chart(fig_sens, width='stretch')

# ── Executive summary ─────────────────────────────────────────────────────────
if summary:
    st.markdown("---")
    st.subheader("Executive Summary - Trained Model Results")

    total_sav = sum(v.get("annual_savings", 0) or 0 for v in summary.values())
    total_leg = sum(v.get("legacy_cost",    0) or 0 for v in summary.values())
    total_ml  = sum(v.get("ml_cost",        0) or 0 for v in summary.values())

    ex1, ex2, ex3, ex4 = st.columns(4)
    ex1.metric("Total savings / year", f"${total_sav:,.0f}")
    ex2.metric("Total legacy cost",    f"${total_leg:,.0f}")
    ex3.metric("Total ML cost",        f"${total_ml:,.0f}")
    ex4.metric("Global ROI",           f"{round(total_sav/max(total_leg,1)*100,1)} %")

    rows_exec = []
    for task, info in summary.items():
        rows_exec.append({
            "Module":       info.get("module", task),
            "AUC-ROC":      info.get("auc_roc", "-"),
            "Gini":         info.get("gini",    "-"),
            "Recall":       f"{(info.get('recall') or 0):.1%}",
            "Legacy Cost":  f"${info.get('legacy_cost',0) or 0:,.0f}",
            "ML Cost":      f"${info.get('ml_cost',0) or 0:,.0f}",
            "Savings/year": f"${info.get('annual_savings',0) or 0:,.0f}",
            "ROI %":        f"{info.get('roi_pct',0) or 0} %",
            "Dataset":      f"{info.get('dataset_rows',0) or 0:,} obs.",
            "Last run":     (info.get("timestamp") or "")[:10],
        })
    st.dataframe(pd.DataFrame(rows_exec), hide_index=True, width='stretch')

st.markdown("---")
st.markdown("""
### Cost Optimization Levers

| Lever | ROI Impact | How to activate |
|---|---|---|
| Cost-optimal threshold | Major | `threshold_cost` in the report |
| SMOTE + resampling | High | `smote_strategy` in `config/fraud.yaml` |
| Feature engineering | High | Add `features.engineered` entries in YAML |
| Monthly retraining | High | Re-run `pipelines/run_all.py` |
| XGBoost + LightGBM stacking | Medium | Add algorithm in `model.algorithm` |
| Real-time scoring (API) | Major | FastAPI wrapper on `load_champion()` |
""")

st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#64748b; font-size:13px; padding:10px 0;'>"
    "BankRisk AI Engine &nbsp;|&nbsp; Config: config/fraud.yaml + config/credit.yaml"
    " &nbsp;|&nbsp; Registry: models/registry.json<br>"
    "<strong>Designed by Oswald Jaures KOFFI</strong></div>",
    unsafe_allow_html=True,
)
