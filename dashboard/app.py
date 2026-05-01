import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.core.registry import ModelRegistry
from dashboard.components.navbar import render_navbar

st.set_page_config(
    page_title="BankRisk AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.kpi { background:linear-gradient(135deg,#1e293b,#0f172a);
       border-radius:12px; padding:20px 22px;
       border-left:4px solid #3b82f6; color:#fff; margin-bottom:6px; }
.kpi.g { border-left-color:#22c55e; }
.kpi.o { border-left-color:#f59e0b; }
.kpi .lbl { font-size:11px; font-weight:600; color:#94a3b8;
            text-transform:uppercase; letter-spacing:1px; }
.kpi .val { font-size:26px; font-weight:800; color:#f8fafc; margin:4px 0; }
.kpi .sub { font-size:12px; color:#64748b; }
.dlt-pos { color:#22c55e; }
.sec { font-size:19px; font-weight:700; color:#1e293b;
       border-bottom:3px solid #3b82f6; padding-bottom:7px; margin:28px 0 14px; }
.formula { background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px;
           padding:13px 16px; font-family:monospace; font-size:13px;
           color:#334155; margin:8px 0; line-height:1.7; }
.footer { text-align:center; color:#64748b; font-size:13px;
          padding:18px 0 8px; border-top:1px solid #e2e8f0; margin-top:32px; }
[data-testid="collapsedControl"] { display:none; }
</style>
""", unsafe_allow_html=True)

render_navbar()

# ── Load registry ─────────────────────────────────────────────────────────────
registry = ModelRegistry()
summary  = registry.summary()

if not summary:
    st.error("No trained model found. Run the command below first.")
    st.code("python pipelines/run_all.py", language="bash")
    st.stop()

fraud  = summary.get("fraud",  {})
credit = summary.get("credit", {})

total_savings = sum(v.get("annual_savings", 0) or 0 for v in summary.values())
total_legacy  = sum(v.get("legacy_cost",    0) or 0 for v in summary.values())

# ── Header ────────────────────────────────────────────────────────────────────
st.title("AI Risk & Cost Optimization Engine")
st.caption(
    "Last updated - "
    + " | ".join(
        f"{v['module']} : {v['timestamp'][:10]}"
        for v in summary.values() if v.get("timestamp")
    )
)
st.divider()

# ── Global KPIs ───────────────────────────────────────────────────────────────
st.markdown('<div class="sec">Global Business Impact</div>', unsafe_allow_html=True)

cols = st.columns(len(summary) * 2 + 1)
idx  = 0

cols[idx].markdown(f"""
<div class="kpi g">
  <div class="lbl">Total Annual Savings</div>
  <div class="val">${total_savings:,.0f}</div>
  <div class="sub">{len(summary)} active module(s)</div>
</div>""", unsafe_allow_html=True)
idx += 1

for task, info in summary.items():
    sav = info.get("annual_savings", 0) or 0
    roi = info.get("roi_pct",        0) or 0
    cols[idx].markdown(f"""
    <div class="kpi">
      <div class="lbl">{info['module']} Savings</div>
      <div class="val">${sav:,.0f}</div>
      <div class="sub dlt-pos">&#9650; ROI {roi} %</div>
    </div>""", unsafe_allow_html=True)
    idx += 1

    auc = info.get("auc_roc", "-")
    gin = info.get("gini",    "-")
    cols[idx].markdown(f"""
    <div class="kpi o">
      <div class="lbl">AUC-ROC {info['module']}</div>
      <div class="val">{auc}</div>
      <div class="sub">Gini : {gin}</div>
    </div>""", unsafe_allow_html=True)
    idx += 1

st.divider()

# ── Per-module sections ───────────────────────────────────────────────────────
for task, info in summary.items():
    lbl    = info.get("labels", {})
    cost   = info.get("cost_cfg", {})
    shap   = info.get("shap_top", [])

    legacy_cost = info.get("legacy_cost",    0) or 0
    ml_cost     = info.get("ml_cost",        0) or 0
    sav         = info.get("annual_savings", 0) or 0
    roi         = info.get("roi_pct",        0) or 0
    fp_leg      = info.get("fp_legacy",      0) or 0
    fp_ml       = info.get("fp_ml",          0) or 0
    fn_leg      = info.get("fn_legacy",      0) or 0
    fn_ml       = info.get("fn_ml",          0) or 0

    unit_fp_lbl = lbl.get("unit_fp_label", "FP cost")
    unit_fn_lbl = lbl.get("unit_fn_label", "FN cost")
    module_name = info.get("module", task.capitalize())

    st.markdown(f'<div class="sec">{module_name} - Concrete ML Impact</div>',
                unsafe_allow_html=True)

    tab_graph, tab_table, tab_formula, tab_shap, tab_sim = st.tabs([
        "Comparison", "Before / After", "Formulas", "SHAP", "Simulator",
    ])

    # ── Comparison chart ─────────────────────────────────────────────────────
    with tab_graph:
        c_left, c_right = st.columns([2, 1])

        with c_left:
            unit_fp = cost.get("unit_fp", cost.get("cost_per_rejected_good", 0))
            unit_fn = cost.get("unit_fn", 0)

            fig = go.Figure()
            categories = [unit_fp_lbl, unit_fn_lbl, "Total Cost"]
            avant = [fp_leg * unit_fp, fn_leg * unit_fn, legacy_cost]
            apres = [fp_ml  * unit_fp, fn_ml  * unit_fn, ml_cost   ]
            fig.add_trace(go.Bar(
                name="BEFORE - Legacy", x=categories, y=avant,
                marker_color="#ef4444",
                text=[f"${v:,.0f}" for v in avant], textposition="outside",
            ))
            fig.add_trace(go.Bar(
                name="AFTER - ML", x=categories, y=apres,
                marker_color="#22c55e",
                text=[f"${v:,.0f}" for v in apres], textposition="outside",
            ))
            fig.update_layout(
                barmode="group",
                title=f"{module_name} - Annual Costs BEFORE vs AFTER ML",
                yaxis_title="USD / year",
                plot_bgcolor="white", paper_bgcolor="white",
                legend=dict(orientation="h", y=-0.22),
                height=400, yaxis=dict(gridcolor="#f1f5f9"),
                margin=dict(t=50, b=60),
            )
            if sav > 0:
                fig.add_annotation(
                    x=2, y=legacy_cost,
                    text=f"<b>Savings: ${sav:,.0f}</b>",
                    showarrow=True, arrowhead=2, ax=0, ay=-45,
                    font=dict(color="#15803d", size=13), arrowcolor="#15803d",
                )
            st.plotly_chart(fig, width='stretch')

        with c_right:
            auc_val = float(info.get("auc_roc") or 0)
            ks_val  = float(info.get("ks_statistic") or 0)
            gin_val = float(info.get("gini") or 0)

            fig_g = make_subplots(
                rows=2, cols=1,
                specs=[[{"type": "indicator"}], [{"type": "indicator"}]],
                vertical_spacing=0.12,
            )
            fig_g.add_trace(go.Indicator(
                mode="gauge+number", value=auc_val,
                title={"text": "AUC-ROC", "font": {"size": 13}},
                gauge={"axis": {"range": [0.5, 1.0], "tickformat": ".2f"},
                       "bar": {"color": "#3b82f6"},
                       "steps": [{"range": [0.5, 0.70], "color": "#fecaca"},
                                  {"range": [0.70, 0.85], "color": "#fef3c7"},
                                  {"range": [0.85, 1.0],  "color": "#dcfce7"}]},
            ), row=1, col=1)

            second_val   = ks_val if ks_val > 0 else gin_val
            second_label = "KS Statistic" if ks_val > 0 else "Gini"
            second_ref   = 0.40            if ks_val > 0 else 0.60
            fig_g.add_trace(go.Indicator(
                mode="gauge+number", value=second_val,
                title={"text": second_label, "font": {"size": 13}},
                gauge={"axis": {"range": [0, 1.0]},
                       "bar": {"color": "#8b5cf6"},
                       "steps": [{"range": [0, second_ref * 0.75], "color": "#fecaca"},
                                  {"range": [second_ref * 0.75, second_ref], "color": "#fef3c7"},
                                  {"range": [second_ref, 1.0],  "color": "#dcfce7"}],
                       "threshold": {"line": {"color": "#ef4444", "width": 3},
                                     "value": second_ref, "thickness": 0.8}},
            ), row=2, col=1)

            fig_g.update_layout(height=400, margin=dict(t=20, b=10))
            st.plotly_chart(fig_g, width='stretch')
            st.caption(f"Red line = quality threshold ({second_label} > {second_ref})")

    # ── Before / After table ──────────────────────────────────────────────────
    with tab_table:
        rows = [
            ("Volume",               f"{info.get('dataset_rows',0):,} obs.",
             f"{info.get('dataset_rows',0):,} obs.", "-"),
            ("Positive Target Rate", f"{(info.get('fraud_rate',0) or 0):.3%}",
             f"{(info.get('fraud_rate',0) or 0):.3%}", "-"),
            ("-- Model",             "Legacy / static rules",
             f"XGBoost ({task})", ""),
            ("AUC-ROC",              "Baseline",
             str(info.get("auc_roc", "-")), ""),
            ("Gini",                 "Baseline",
             str(info.get("gini", "-")), ""),
            ("Recall",               "~85 %",
             f"{(info.get('recall',0) or 0):.1%}", ""),
            ("-- Counts",            "", "", ""),
            (f"FP / year ({unit_fp_lbl})", f"{fp_leg:,}",
             f"{fp_ml:,}", f"- {fp_leg-fp_ml:,}"),
            (f"FN / year ({unit_fn_lbl})", f"{fn_leg:,}",
             f"{fn_ml:,}", f"- {fn_leg-fn_ml:,}"),
            ("-- Annual Costs",      "", "", ""),
            ("Legacy total cost",    f"${legacy_cost:,.0f}", "-", ""),
            ("ML total cost",        "-", f"${ml_cost:,.0f}", ""),
            ("Annual Savings",       "-", f"${sav:,.0f}", f"ROI {roi} %"),
        ]
        df_t = pd.DataFrame(rows, columns=["Indicator", "BEFORE", "AFTER", "Delta"])
        st.dataframe(df_t, hide_index=True, width='stretch', height=430)

    # ── Formulas ──────────────────────────────────────────────────────────────
    with tab_formula:
        st.markdown(f"#### Full Transparency - {module_name}")
        if task == "fraud":
            u_fp = cost.get("unit_fp", 5)
            u_fn = cost.get("unit_fn", 250)
            vol  = cost.get("annual_volume", 10_000_000)
            bp   = cost.get("baseline_fp_rate", 0.05)
            br   = cost.get("baseline_recall",  0.85)
            fr   = info.get("fraud_rate", 0.0017) or 0.0017
            st.markdown(f"""
<div class="formula">
<b>Legacy Cost</b><br>
  FP = {vol:,} tx &times; (1-{fr:.4f}) &times; {bp:.0%} = <b>{fp_leg:,} alerts</b><br>
  FN = {vol:,} tx &times; {fr:.4f} &times; (1-{br:.0%}) = <b>{fn_leg:,} missed frauds</b><br>
  Cost = {fp_leg:,} &times; ${u_fp} + {fn_leg:,} &times; ${u_fn} = <b>${legacy_cost:,.0f}</b>
<br><br>
<b>ML Cost (F1-optimal threshold = {info.get('threshold_opt','?')})</b><br>
  Extrapolated FP = <b>{fp_ml:,}</b> - Cost = {fp_ml:,} &times; ${u_fp} = ${fp_ml*u_fp:,.0f}<br>
  Extrapolated FN = <b>{fn_ml:,}</b> - Cost = {fn_ml:,} &times; ${u_fn} = ${fn_ml*u_fn:,.0f}<br>
  Total ML cost = <b>${ml_cost:,.0f}</b>
<br><br>
<b>Savings = ${legacy_cost:,.0f} - ${ml_cost:,.0f} = ${sav:,.0f}  (ROI {roi} %)</b>
</div>""", unsafe_allow_html=True)
        else:
            loan = cost.get("avg_loan_amount", 15_000)
            lgd  = cost.get("loss_given_default", 0.45)
            n    = cost.get("annual_applications", 50_000)
            dr   = info.get("fraud_rate", 0.22) or 0.22
            st.markdown(f"""
<div class="formula">
<b>Baseline Loss (approve everyone)</b><br>
  Defaults = {n:,} applications &times; {dr:.2%} = <b>{fn_leg:,} defaults</b><br>
  Loss = {fn_leg:,} &times; ${loan:,} &times; {lgd:.0%} LGD = <b>${legacy_cost:,.0f}</b>
<br><br>
<b>ML Cost</b><br>
  Approved defaults (FN) = <b>{fn_ml:,}</b> - Loss = ${fn_ml*loan*lgd:,.0f}<br>
  Good files rejected (FP) = <b>{fp_ml:,}</b> - Opp. cost = ${fp_ml*cost.get('cost_per_rejected_good',200):,.0f}<br>
  Total ML cost = <b>${ml_cost:,.0f}</b>
<br><br>
<b>Savings = ${legacy_cost:,.0f} - ${ml_cost:,.0f} = ${sav:,.0f}  (ROI {roi} %)</b>
</div>""", unsafe_allow_html=True)

    # ── SHAP ──────────────────────────────────────────────────────────────────
    with tab_shap:
        if shap:
            df_shap = pd.DataFrame(shap)
            fig_shap = go.Figure(go.Bar(
                x=df_shap["mean_shap"], y=df_shap["feature"],
                orientation="h",
                marker=dict(
                    color=df_shap["mean_shap"],
                    colorscale="Blues" if task == "fraud" else "Oranges",
                    showscale=False,
                ),
                text=[f"{v:.4f}" for v in df_shap["mean_shap"]],
                textposition="outside",
            ))
            fig_shap.update_layout(
                title=f"Top Features - {module_name} (Mean |SHAP|)",
                xaxis_title="Mean |SHAP value|",
                yaxis=dict(autorange="reversed"),
                plot_bgcolor="white", paper_bgcolor="white",
                height=420, margin=dict(l=160, t=50),
            )
            st.plotly_chart(fig_shap, width='stretch')
            st.caption("Higher SHAP value = greater feature influence on the prediction.")
        else:
            st.info("SHAP not available. Re-run the pipeline.")

    # ── Simulator ─────────────────────────────────────────────────────────────
    with tab_sim:
        st.markdown(f"#### What-If Simulator - {module_name}")
        s1, s2 = st.columns([1, 2])

        with s1:
            if task == "fraud":
                sim_vol   = st.number_input("Annual volume", value=int(cost.get("annual_volume", 10_000_000)),
                                             step=1_000_000, format="%d", key=f"vol_{task}")
                sim_ufp   = st.number_input("Cost / false alert ($)", value=int(cost.get("unit_fp", 5)),
                                             step=1, key=f"ufp_{task}")
                sim_ufn   = st.number_input("Loss / missed fraud ($)", value=int(cost.get("unit_fn", 250)),
                                             step=10, key=f"ufn_{task}")
                sim_fp_rt = st.slider("ML FP Rate (%)", 0.1, 5.0, 0.8, 0.1, key=f"fpr_{task}") / 100
                sim_rec   = st.slider("ML Recall (%)", 50, 99, int((info.get("recall") or 0.9)*100),
                                       1, key=f"rec_{task}") / 100
                fr        = info.get("fraud_rate", 0.0017) or 0.0017
                bp        = cost.get("baseline_fp_rate", 0.05)
                br        = cost.get("baseline_recall",  0.85)
                leg_fp_s  = int(sim_vol * (1-fr) * bp)
                leg_fn_s  = int(sim_vol * fr * (1-br))
                leg_c_s   = leg_fp_s * sim_ufp + leg_fn_s * sim_ufn
                ml_fp_s   = int(sim_vol * (1-fr) * sim_fp_rt)
                ml_fn_s   = int(sim_vol * fr * (1-sim_rec))
                ml_c_s    = ml_fp_s * sim_ufp + ml_fn_s * sim_ufn
                sav_s     = leg_c_s - ml_c_s
            else:
                sim_apps  = st.number_input("Applications / year", value=int(cost.get("annual_applications", 50_000)),
                                             step=5_000, format="%d", key=f"apps_{task}")
                sim_loan  = st.number_input("Average loan ($)", value=int(cost.get("avg_loan_amount", 15_000)),
                                             step=1_000, key=f"loan_{task}")
                sim_lgd   = st.slider("LGD (%)", 20, 70, int(cost.get("loss_given_default", 0.45)*100),
                                       5, key=f"lgd_{task}") / 100
                sim_dr    = st.slider("Default rate (%)", 5, 40, int((info.get("fraud_rate") or 0.22)*100),
                                       1, key=f"dr_{task}") / 100
                sim_rec   = st.slider("ML Recall (%)", 50, 95,
                                       int((info.get("recall") or 0.80)*100), 1, key=f"rec_{task}") / 100
                leg_c_s   = int(sim_apps * sim_dr) * sim_loan * sim_lgd
                ml_fn_s   = int(sim_apps * sim_dr * (1 - sim_rec))
                ml_c_s    = ml_fn_s * sim_loan * sim_lgd
                sav_s     = leg_c_s - ml_c_s
                leg_fp_s  = int(sim_apps * sim_dr)
                ml_fp_s   = ml_fn_s

        with s2:
            sm1, sm2, sm3 = st.columns(3)
            sm1.metric("Legacy / year",  f"${leg_c_s:,.0f}")
            sm2.metric("ML / year",      f"${ml_c_s:,.0f}",  f"-${leg_c_s-ml_c_s:,.0f}")
            sm3.metric("Savings",        f"${sav_s:,.0f}",
                       f"ROI {round(sav_s/max(leg_c_s,1)*100,1)} %")

            cats_s = [unit_fp_lbl, unit_fn_lbl, "Total"]
            fig_s  = go.Figure()
            fp_val_leg = leg_fp_s * (sim_ufp if task == "fraud" else sim_loan * sim_lgd if task != "fraud" else 0)
            fn_val_leg = (leg_fn_s * (sim_ufn if task == "fraud" else sim_loan * sim_lgd)) if task == "fraud" else leg_c_s - fp_val_leg
            fp_val_ml  = ml_fp_s  * (sim_ufp if task == "fraud" else cost.get("cost_per_rejected_good", 200))
            fn_val_ml  = ml_fn_s  * (sim_ufn if task == "fraud" else sim_loan * sim_lgd)

            fig_s.add_trace(go.Bar(name="Legacy", x=cats_s, y=[fp_val_leg, fn_val_leg, leg_c_s],
                                    marker_color="#ef4444",
                                    text=[f"${v:,.0f}" for v in [fp_val_leg, fn_val_leg, leg_c_s]],
                                    textposition="outside"))
            fig_s.add_trace(go.Bar(name="ML", x=cats_s, y=[fp_val_ml, fn_val_ml, ml_c_s],
                                    marker_color="#22c55e",
                                    text=[f"${v:,.0f}" for v in [fp_val_ml, fn_val_ml, ml_c_s]],
                                    textposition="outside"))
            fig_s.update_layout(
                barmode="group", height=300,
                plot_bgcolor="white", paper_bgcolor="white",
                yaxis_title="USD", yaxis=dict(gridcolor="#f1f5f9"),
                legend=dict(orientation="h", y=-0.28),
                margin=dict(t=20, b=60),
            )
            st.plotly_chart(fig_s, width='stretch')

    st.divider()

# ── Global waterfall ──────────────────────────────────────────────────────────
st.markdown('<div class="sec">Savings Breakdown - Global View</div>', unsafe_allow_html=True)

wf_x = ["Total Legacy Cost"]
wf_y = [total_legacy]
wf_m = ["absolute"]
wf_t = [f"${total_legacy:,.0f}"]

for task, info in summary.items():
    fp_leg_ = info.get("fp_legacy", 0) or 0
    fp_ml_  = info.get("fp_ml",     0) or 0
    fn_leg_ = info.get("fn_legacy",  0) or 0
    fn_ml_  = info.get("fn_ml",      0) or 0
    cost_   = info.get("cost_cfg",   {})
    u_fp_   = cost_.get("unit_fp") or cost_.get("cost_per_rejected_good") or 0
    u_fn_   = cost_.get("unit_fn") or 0

    if (fp_leg_ - fp_ml_) * u_fp_ > 0:
        lbl = info.get("labels", {}).get("unit_fp_label", f"FP {task}")
        wf_x.append(f"- {lbl} ({task})")
        wf_y.append(-((fp_leg_ - fp_ml_) * u_fp_))
        wf_m.append("relative")
        wf_t.append(f"-${(fp_leg_-fp_ml_)*u_fp_:,.0f}")

    if (fn_leg_ - fn_ml_) * u_fn_ > 0:
        lbl = info.get("labels", {}).get("unit_fn_label", f"FN {task}")
        wf_x.append(f"- {lbl} ({task})")
        wf_y.append(-((fn_leg_ - fn_ml_) * u_fn_))
        wf_m.append("relative")
        wf_t.append(f"-${(fn_leg_-fn_ml_)*u_fn_:,.0f}")

total_ml = sum(v.get("ml_cost", 0) or 0 for v in summary.values())
wf_x.append("Residual ML Cost")
wf_y.append(0)
wf_m.append("total")
wf_t.append(f"${total_ml:,.0f}")

fig_wf = go.Figure(go.Waterfall(
    orientation="v", measure=wf_m, x=wf_x, y=wf_y, text=wf_t,
    textposition="outside",
    connector={"line": {"color": "#94a3b8"}},
    decreasing={"marker": {"color": "#22c55e"}},
    increasing={"marker": {"color": "#ef4444"}},
    totals={"marker": {"color": "#3b82f6"}},
))
fig_wf.update_layout(
    title=f"Where does each saved dollar come from? - Total: ${total_savings:,.0f} / year",
    height=420, plot_bgcolor="white", paper_bgcolor="white",
    yaxis_title="USD", yaxis=dict(gridcolor="#f1f5f9"),
    margin=dict(t=50, b=80),
)
st.plotly_chart(fig_wf, width='stretch')

# ── Training history ──────────────────────────────────────────────────────────
st.markdown('<div class="sec">Training History</div>', unsafe_allow_html=True)

hist_cols = st.columns(len(summary))
for i, (task, info) in enumerate(summary.items()):
    hist = info.get("history", [])
    if hist:
        df_h = pd.DataFrame(hist)
        df_h["timestamp"] = pd.to_datetime(df_h["timestamp"]).dt.strftime("%Y-%m-%d %H:%M")
        with hist_cols[i]:
            st.caption(f"**{info['module']}** - {len(hist)} run(s)")
            st.dataframe(df_h[["timestamp","auc_roc","gini","annual_savings"]].tail(5),
                         hide_index=True, width='stretch')

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  BankRisk AI Engine &nbsp;|&nbsp; XGBoost + SMOTE + SHAP &nbsp;|&nbsp; Streamlit<br>
  <strong>Designed by Oswald Jaures KOFFI</strong>
</div>
""", unsafe_allow_html=True)
