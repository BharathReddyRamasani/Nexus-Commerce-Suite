import streamlit as st
import time
from nexus_commerce.common.supabase_client import check_connection
from nexus_commerce.auth import logic as auth_logic
from nexus_commerce.common._utils import inject_custom_css

# ── Page Configuration ──
st.set_page_config(
    page_title="Nexus Commerce Suite",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

inject_custom_css()

# ── Connection Check ──
try:
    check_connection()
except (ValueError, ConnectionError) as e:
    st.error(f"**FATAL ERROR:** Could not connect to the database.", icon="🔥")
    st.error(f"Details: {e}")
    st.stop()

# ── Database Table Check ──
from nexus_commerce.common.db_setup import check_tables_exist, get_setup_sql
table_status = check_tables_exist()
missing_tables = [t for t, exists in table_status.items() if not exists]

if missing_tables:
    st.markdown(f"""
    <div style="
        background: rgba(245, 158, 11, 0.05);
        border-left: 5px solid #f59e0b;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
    ">
        <h3 style="color: #f59e0b; margin: 0 0 0.5rem 0;">🏗️ Database Setup Required</h3>
        <p style="color: rgba(226, 232, 240, 0.7); margin: 0; font-size: 0.9rem;">
            The enterprise suite is connected, but <strong>{len(missing_tables)} metadata tables</strong> are missing: 
            <code>{', '.join(missing_tables)}</code>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_guide, col_sql = st.columns([1, 1.5], gap="large")
    
    with col_guide:
        st.markdown("""
        #### 📋 Integration Steps
        1. Open your [Supabase Dashboard](https://supabase.com/dashboard)
        2. Navigate to **SQL Editor** → **New Query**
        3. Paste the enterprise schema from the right
        4. Click **Run** and **Refresh** this page
        """)
        if st.button("🔄 Refresh Application State", type="primary", use_container_width=True):
            st.rerun()

    with col_sql:
        with st.expander("📄 Click to View Complete Enterprise SQL", expanded=True):
            st.code(get_setup_sql(), language="sql")
    st.stop()

# ── Session State ──
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_email = ""

# ── Already Logged In ──
if st.session_state.authenticated:
    st.success(f"Verified Session: **{st.session_state.user_email}**", icon="🛡️")
    if st.button("Go to Dashboard →", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Dashboard.py")
    st.stop()

# ── Split Layout ──
col_styled, col_form = st.columns([1.4, 1], gap="large")

with col_styled:
    # ── Premium 3D Branding ──
    branding_html = """<div class="perspective-box">
<div class="card-3d">
<div class="glow-orb" style="top: -100px; right: -100px; opacity: 0.3;"></div>
<div class="glow-orb" style="bottom: -100px; left: -100px; opacity: 0.2; width: 400px; height: 400px;"></div>
<div class="content-3d">
<div class="hero-icon-3d">🛒</div>
<h1 class="hero-title-3d">Nexus<br>Commerce</h1>
<p class="hero-subtitle">Industrial Business Management Suite</p>
<div class="hero-line"></div>
<p class="hero-tagline">Scaling your enterprise with intelligence, automation, and world-class aesthetics.</p>
<div class="feature-stack-3d">
<div class="feature-item-3d">
<div class="feature-icon-glass">🎯</div>
<div>
<strong>Net Profit Engine</strong>
<span>Real-time overhead & tax optimization.</span>
</div>
</div>
<div class="feature-item-3d">
<div class="feature-icon-glass">🔮</div>
<div>
<strong>Predictive Intelligence</strong>
<span>AI-driven forecasting & stock flows.</span>
</div>
</div>
<div class="feature-item-3d">
<div class="feature-icon-glass">📊</div>
<div>
<strong>Industrial BI</strong>
<span>ABC, RFM, and Pareto Analytics.</span>
</div>
</div>
</div>
</div>
</div>
</div>
<style>
.perspective-box {
    perspective: 2500px;
    padding: 20px;
    height: 750px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.card-3d {
    background: linear-gradient(145deg, rgba(99,102,241,0.25), rgba(139,92,246,0.1));
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 40px;
    width: 100%;
    height: 100%;
    position: relative;
    overflow: hidden;
    transform: rotateY(-15deg) rotateX(5deg);
    transform-style: preserve-3d;
    transition: all 1s cubic-bezier(0.2, 1, 0.2, 1);
    box-shadow: -50px 50px 100px rgba(0,0,0,0.6);
    padding: 3.5rem;
}
.card-3d:hover {
    transform: rotateY(0deg) rotateX(0deg) scale(1.03) translateZ(50px);
    box-shadow: 0 60px 120px rgba(0,0,0,0.8);
    border-color: #8b5cf6;
}
.glow-orb {
    position: absolute;
    width: 350px;
    height: 350px;
    background: radial-gradient(circle, #6366f1 0%, transparent 70%);
    border-radius: 50%;
    filter: blur(80px);
    z-index: 0;
}
.content-3d {
    position: relative;
    z-index: 2;
    transform: translateZ(60px);
}
.hero-icon-3d {
    font-size: 6.5rem;
    margin-bottom: 2rem;
    animation: float-icon-3d 6s ease-in-out infinite;
    filter: drop-shadow(0 0 45px rgba(99,102,241,0.8));
    transform: translateZ(100px);
}
.hero-title-3d {
    font-family: 'Inter', sans-serif;
    font-weight: 950;
    font-size: 5.2rem;
    background: linear-gradient(135deg, #fff 10%, #c4b5fd 50%, #6366f1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 0.85;
    letter-spacing: -0.07em;
    margin: 0;
    transform: translateZ(80px);
}
.hero-subtitle {
    color: #c4b5fd;
    text-transform: uppercase;
    font-weight: 850;
    font-size: 1rem;
    letter-spacing: 0.45em;
    margin-top: 1.5rem;
    margin-bottom: 1.5rem;
    transform: translateZ(60px);
}
.hero-line {
    width: 100px;
    height: 6px;
    background: linear-gradient(90deg, #8b5cf6, transparent);
    border-radius: 3px;
    margin-bottom: 1.5rem;
    transform: translateZ(50px);
}
.hero-tagline {
    color: rgba(226, 232, 240, 0.7);
    font-size: 1.2rem;
    line-height: 1.7;
    max-width: 480px;
    margin-bottom: 3.5rem;
    transform: translateZ(40px);
}
.feature-item-3d {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    padding: 1.6rem;
    border-radius: 30px;
    display: flex;
    align-items: center;
    gap: 1.6rem;
    transition: all 0.6s cubic-bezier(0.19, 1, 0.22, 1);
    backdrop-filter: blur(20px);
    transform: translateZ(30px);
}
.feature-item-3d:hover {
    background: rgba(255,255,255,0.12);
    transform: translateZ(150px) scale(1.08) translateX(25px);
    border-color: #8b5cf6;
    box-shadow: 0 30px 60px rgba(0,0,0,0.5);
}
.feature-icon-glass {
    font-size: 2.2rem;
    width: 65px;
    height: 65px;
    background: rgba(99,102,241,0.25);
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.feature-item-3d strong {
    color: #fff;
    display: block;
    font-size: 1.25rem;
}
.feature-item-3d span {
    color: rgba(226,232,240,0.5);
    font-size: 0.95rem;
}
@keyframes float-icon-3d {
    0%, 100% { transform: translateZ(100px) translateY(0px) rotateY(0deg); }
    50% { transform: translateZ(160px) translateY(-30px) rotateY(20deg); }
}
</style>"""
    st.html(branding_html)

with col_form:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    # ── Login / Register Tabs ──
    login_tab, register_tab = st.tabs(["🔑 **Sign In**", "📋 **Create Account**"])

    with login_tab:
        with st.form("login_form"):
            st.markdown('<div class="section-header">Executive Portal</div>', unsafe_allow_html=True)
            email = st.text_input("Corporate Email", placeholder="you@company.com")
            password = st.text_input("Access Key", type="password", placeholder="••••••••")
            login_submitted = st.form_submit_button("Authenticate →", use_container_width=True, type="primary")

            if login_submitted:
                if not email or not password:
                    st.error("Missing credentials.", icon="🚨")
                else:
                    with st.spinner("Verifying credentials…"):
                        response = auth_logic.sign_in(email, password)
                    if response['success']:
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        st.success("Access Granted. Initializing...", icon="✅")
                        time.sleep(1)
                        st.switch_page("pages/1_Dashboard.py")
                    else:
                        st.error(response['message'], icon="🚨")

    with register_tab:
        with st.form("register_form"):
            st.markdown('<div class="section-header">Enterprise Registration</div>', unsafe_allow_html=True)
            new_email = st.text_input("Official Email", key="reg_email", placeholder="you@company.com")
            new_password = st.text_input("Access Key (min. 6 chars)", type="password", key="reg_pass", placeholder="••••••••")
            confirm_password = st.text_input("Confirm Access Key", type="password", key="reg_pass_confirm", placeholder="••••••••")
            register_submitted = st.form_submit_button("Request Access", use_container_width=True)

            if register_submitted:
                if not new_email or not new_password:
                    st.error("Incomplete data.", icon="🚨")
                elif new_password != confirm_password:
                    st.error("Keys do not match.", icon="🚨")
                else:
                    with st.spinner("Processing request…"):
                        response = auth_logic.sign_up(new_email, new_password)
                    if response['success']:
                        st.success(response['message'], icon="✅")
                        st.info("You may now proceed to the Sign In portal.", icon="ℹ️")
                    else:
                        st.error(response['message'], icon="🚨")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background: rgba(99,102,241,0.05); border: 1px solid rgba(99,102,241,0.1); border-radius: 16px; padding: 1rem; color: rgba(226,232,240,0.4); font-size: 0.8rem;">
        🛡️ <strong>Encrypted Session</strong><br>
        Your session is secured with Supabase Auth & Industry-standard RLS protocols.
    </div>
    """, unsafe_allow_html=True)

# ── Feature Highlights ──
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-header" style="text-align:center;">Why Nexus Commerce?</div>', unsafe_allow_html=True)

fcol1, fcol2, fcol3 = st.columns(3)
with fcol1:
    st.markdown("""
    <div class="action-card">
        <div class="action-icon">📊</div>
        <div class="action-title">Real-time Analytics</div>
        <div class="action-desc">AI-powered forecasting, ABC analysis & RFM segmentation</div>
    </div>
    """, unsafe_allow_html=True)
with fcol2:
    st.markdown("""
    <div class="action-card">
        <div class="action-icon">🛡️</div>
        <div class="action-title">Enterprise Security</div>
        <div class="action-desc">Supabase auth, RLS policies & encrypted credentials</div>
    </div>
    """, unsafe_allow_html=True)
with fcol3:
    st.markdown("""
    <div class="action-card">
        <div class="action-icon">⚡</div>
        <div class="action-title">Full-Stack CRUD</div>
        <div class="action-desc">Complete inventory, sales, CRM & reporting operations</div>
    </div>
    """, unsafe_allow_html=True)

# ── Footer ──
st.markdown("""
<div style="
    text-align: center;
    margin-top: 2rem;
    padding: 1rem;
    color: rgba(226, 232, 240, 0.2);
    font-size: 0.7rem;
    font-family: 'Inter', sans-serif;
    letter-spacing: 0.05em;
">
    &copy; 2026 Nexus Commerce Suite &mdash; Industrial-Grade Business Management Platform
</div>
""", unsafe_allow_html=True)
