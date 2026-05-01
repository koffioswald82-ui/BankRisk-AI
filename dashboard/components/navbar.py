import streamlit as st


def render_navbar():
    st.markdown("""
    <style>
    .topnav {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        padding: 14px 24px;
        border-radius: 10px;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
    }
    .topnav-brand {
        font-size: 17px;
        font-weight: 800;
        color: #f8fafc;
        margin-right: 40px;
        letter-spacing: -0.3px;
    }
    .topnav-sub {
        font-size: 11px;
        color: #64748b;
        font-weight: 500;
        letter-spacing: 0.5px;
    }
    /* Page links inside navbar columns */
    div[data-testid="stPageLink"] a {
        font-weight: 600 !important;
        font-size: 13px !important;
    }
    </style>
    <div class="topnav">
        <div>
            <div class="topnav-brand">BankRisk AI</div>
            <div class="topnav-sub">AI RISK &amp; COST OPTIMIZATION ENGINE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.page_link("app.py",                       label="Executive Dashboard")
    with c2:
        st.page_link("pages/1_Fraud_Detection.py",   label="Fraud Detection")
    with c3:
        st.page_link("pages/2_Credit_Risk.py",       label="Credit Risk")
    with c4:
        st.page_link("pages/3_Cost_Optimization.py", label="Cost Simulator")
    st.divider()
