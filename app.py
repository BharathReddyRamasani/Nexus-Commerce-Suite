import streamlit as st
import time
from nexus_commerce.common.supabase_client import check_connection
from nexus_commerce.auth import logic as auth_logic
from nexus_commerce.common._utils import inject_custom_css

# ── Page Configuration ──
st.set_page_config(
    page_title="Nexus Commerce Suite",
    page_icon="🛒",
    layout="centered",
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
    st.warning(f"⚠️ **Database Setup Required** — {len(missing_tables)} table(s) are missing: `{'`, `'.join(missing_tables)}`", icon="⚠️")
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(245,158,11,0.1), rgba(239,68,68,0.05));
        border: 1px solid rgba(245,158,11,0.3);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin: 1rem 0;
    ">
        <div style="font-weight: 700; font-size: 1.1rem; color: #f59e0b; margin-bottom: 0.8rem;">📋 Quick Setup Guide</div>
        <div style="color: rgba(226,232,240,0.8); font-size: 0.88rem; line-height: 1.7;">
            <strong>Step 1:</strong> Go to your <a href="https://supabase.com/dashboard" target="_blank" style="color: #8b5cf6;">Supabase Dashboard</a><br>
            <strong>Step 2:</strong> Open <strong>SQL Editor</strong> → Click <strong>New Query</strong><br>
            <strong>Step 3:</strong> Copy the SQL below and paste it in the editor<br>
            <strong>Step 4:</strong> Click <strong>Run</strong> (the green play button)<br>
            <strong>Step 5:</strong> Come back here and <strong>refresh this page</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📄 Click to view the complete SQL (copy all of it)", expanded=True):
        st.code(get_setup_sql(), language="sql")

    st.info("👆 Copy the SQL above, run it in Supabase SQL Editor, then refresh this page.", icon="🔄")
    st.stop()

# ── Session State ──
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_email = ""

# ── Already Logged In ──
if st.session_state.authenticated:
    st.success(f"You are already logged in as **{st.session_state.user_email}**.", icon="✅")
    if st.button("Go to Dashboard →", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Dashboard.py")
    st.stop()

# ── Premium Login Hero ──
st.markdown("""
<div style="text-align: center; margin: 1.5rem 0 0.5rem 0;">
    <div style="
        display: inline-block;
        font-size: 4.5rem;
        margin-bottom: 0.5rem;
        animation: float 3s ease-in-out infinite;
        filter: drop-shadow(0 0 20px rgba(99,102,241,0.4));
    ">🛒</div>
    <h1 style="
        font-family: 'Inter', sans-serif;
        font-weight: 900;
        font-size: 2.8rem;
        background: linear-gradient(135deg, #6366f1, #8b5cf6, #a78bfa, #c4b5fd);
        background-size: 300% auto;
        animation: shimmer 4s linear infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
        letter-spacing: -0.04em;
        line-height: 1.1;
    ">Nexus Commerce</h1>
    <p style="
        color: rgba(226, 232, 240, 0.4);
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        font-weight: 500;
        letter-spacing: 0.2em;
        text-transform: uppercase;
    ">Enterprise Business Management Suite</p>
</div>
<style>
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-12px); }
}
@keyframes shimmer {
    0% { background-position: 0% center; }
    100% { background-position: 300% center; }
}
</style>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Login / Register Tabs ──
login_tab, register_tab = st.tabs(["🔑 **Sign In**", "📋 **Create Account**"])

with login_tab:
    with st.form("login_form"):
        st.markdown('<div class="section-header">Welcome Back</div>', unsafe_allow_html=True)
        email = st.text_input("Email Address", placeholder="you@company.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        login_submitted = st.form_submit_button("Sign In →", use_container_width=True, type="primary")

        if login_submitted:
            if not email or not password:
                st.error("Please enter both email and password.", icon="🚨")
            else:
                with st.spinner("Authenticating…"):
                    response = auth_logic.sign_in(email, password)
                if response['success']:
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.success("Login successful! Redirecting…", icon="✅")
                    time.sleep(1)
                    st.switch_page("pages/1_Dashboard.py")
                else:
                    st.error(response['message'], icon="🚨")

with register_tab:
    with st.form("register_form"):
        st.markdown('<div class="section-header">Create Your Account</div>', unsafe_allow_html=True)
        new_email = st.text_input("Email Address", key="reg_email", placeholder="you@company.com")
        new_password = st.text_input("Password (min. 6 characters)", type="password", key="reg_pass", placeholder="••••••••")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_pass_confirm", placeholder="••••••••")
        register_submitted = st.form_submit_button("Create Account", use_container_width=True)

        if register_submitted:
            if not new_email or not new_password:
                st.error("Please enter both email and password.", icon="🚨")
            elif new_password != confirm_password:
                st.error("Passwords do not match.", icon="🚨")
            else:
                with st.spinner("Creating account…"):
                    response = auth_logic.sign_up(new_email, new_password)
                if response['success']:
                    st.success(response['message'], icon="✅")
                    st.info("You can now sign in using the Login tab.", icon="ℹ️")
                else:
                    st.error(response['message'], icon="🚨")

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
