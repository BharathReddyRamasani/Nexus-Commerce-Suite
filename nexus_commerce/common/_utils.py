"""
Nexus Commerce Suite — Shared UI Utilities (World-Class Edition)
=================================================================
Centralized helpers for authentication guards, sidebar rendering,
and the premium dark-mode CSS theme used across all pages.
"""
import streamlit as st


# ────────────────────────────────────────────
#  Authentication Guard
# ────────────────────────────────────────────
def require_auth():
    """Redirect unauthenticated users to login page."""
    if not st.session_state.get("authenticated"):
        st.error("🔒 **Access Denied** — You must be logged in to view this page.")
        st.stop()


# ────────────────────────────────────────────
#  Premium Sidebar with Navigation
# ────────────────────────────────────────────
def render_sidebar():
    """Render a consistent premium sidebar with nav across all pages."""
    with st.sidebar:
        # Brand
        st.markdown("""
        <div style="text-align:center; padding: 1.2rem 0 0.5rem 0;">
            <div style="
                font-size: 2.8rem;
                animation: pulse-glow 2s ease-in-out infinite;
            ">🛒</div>
            <div style="
                font-family: 'Inter', sans-serif;
                font-weight: 900;
                font-size: 1.15rem;
                background: linear-gradient(135deg, #6366f1, #8b5cf6, #a78bfa);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                letter-spacing: -0.02em;
                margin-top: 0.3rem;
            ">NEXUS COMMERCE</div>
            <div style="
                font-size: 0.6rem;
                color: rgba(226,232,240,0.35);
                text-transform: uppercase;
                letter-spacing: 0.2em;
                margin-top: 0.2rem;
            ">Enterprise Suite v2.0</div>
        </div>
        """, unsafe_allow_html=True)

        # User card
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(139,92,246,0.08));
            border: 1px solid rgba(99,102,241,0.2);
            border-radius: 12px;
            padding: 0.75rem 1rem;
            margin: 0.5rem 0 1rem 0;
            text-align: center;
        ">
            <div style="font-size: 1.5rem; margin-bottom: 0.2rem;">👤</div>
            <div style="font-size: 0.65rem; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 0.12em;">logged in as</div>
            <div style="font-size: 0.82rem; color: rgba(255,255,255,0.9); font-weight: 600; margin-top: 0.15rem;">{st.session_state.get('user_email', 'User')}</div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation
        st.markdown("""
        <div style="
            font-size: 0.65rem;
            color: rgba(226,232,240,0.35);
            text-transform: uppercase;
            letter-spacing: 0.15em;
            font-weight: 700;
            padding: 0 0 0.4rem 0.5rem;
        ">Navigation</div>
        """, unsafe_allow_html=True)

        nav_items = [
            ("📊", "Dashboard", "pages/1_Dashboard.py"),
            ("📦", "Inventory", "pages/2_Inventory_Management.py"),
            ("🛒", "Sales Terminal", "pages/3_Record_Sale.py"),
            ("👥", "Customers", "pages/4_Customer_Management.py"),
            ("📈", "Reports", "pages/5_Reports.py"),
            ("🔬", "Analytics (DS)", "pages/6_Analytics.py"),
            ("💸", "Expenses", "pages/7_Expense_Management.py"),
        ]
        for icon, label, page in nav_items:
            if st.button(f"{icon}  {label}", use_container_width=True, key=f"nav_{label}"):
                st.switch_page(page)

        st.divider()

        if st.button("🚪  Sign Out", use_container_width=True, key="sidebar_logout"):
            st.session_state.authenticated = False
            st.session_state.user_email = ""
            st.switch_page("app.py")


# ────────────────────────────────────────────
#  Premium Dark-Mode CSS Theme (World-Class)
# ────────────────────────────────────────────
def inject_custom_css():
    """Inject the world-class dark-mode glassmorphic CSS theme."""
    st.markdown("""
    <style>
    /* ── Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ── Root Variables ── */
    :root {
        --bg-primary: #0a0a14;
        --bg-secondary: #12121f;
        --bg-card: rgba(18, 18, 31, 0.75);
        --glass-border: rgba(99, 102, 241, 0.12);
        --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        --text-primary: #e2e8f0;
        --text-secondary: rgba(226, 232, 240, 0.55);
        --accent-primary: #6366f1;
        --accent-secondary: #8b5cf6;
        --accent-gradient: linear-gradient(135deg, #6366f1, #8b5cf6, #a78bfa);
        --accent-glow: rgba(99, 102, 241, 0.4);
        --success: #10b981;
        --success-glow: rgba(16, 185, 129, 0.3);
        --warning: #f59e0b;
        --danger: #ef4444;
        --info: #3b82f6;
        --radius: 16px;
        --radius-sm: 10px;
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        --transition-fast: all 0.15s ease;
    }

    /* ── Animations ── */
    @keyframes pulse-glow {
        0%, 100% { filter: drop-shadow(0 0 8px rgba(99,102,241,0.3)); }
        50% { filter: drop-shadow(0 0 20px rgba(99,102,241,0.6)); }
    }
    @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes gradient-shift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    /* ── Global ── */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }

    /* Animated gradient mesh background */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background:
            radial-gradient(ellipse at 20% 50%, rgba(99,102,241,0.08) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 20%, rgba(139,92,246,0.06) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 80%, rgba(59,130,246,0.04) 0%, transparent 50%);
        background-size: 200% 200%;
        animation: gradient-shift 15s ease infinite;
        pointer-events: none;
        z-index: 0;
    }

    .block-container {
        padding-top: 2rem !important;
        max-width: 1280px !important;
        position: relative;
        z-index: 1;
    }

    /* ── Typography ── */
    h1, h2, h3, h4 {
        font-family: 'Inter', sans-serif !important;
        color: var(--text-primary) !important;
    }
    h1 { font-weight: 800 !important; letter-spacing: -0.03em !important; font-size: 1.8rem !important; }
    h2 { font-weight: 700 !important; letter-spacing: -0.02em !important; }
    h3 { font-weight: 600 !important; }
    p, span, label, div { font-family: 'Inter', sans-serif !important; }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a14 0%, #0f1128 50%, #12121f 100%) !important;
        border-right: 1px solid var(--glass-border) !important;
    }

    /* ★ HIDE Streamlit's default page navigation ★ */
    [data-testid="stSidebarNav"],
    section[data-testid="stSidebar"] nav,
    section[data-testid="stSidebar"] ul {
        display: none !important;
        height: 0 !important;
        overflow: hidden !important;
    }

    /* Hide Streamlit branding & footer */
    #MainMenu, footer, header[data-testid="stHeader"] {
        visibility: hidden !important;
        height: 0 !important;
    }

    /* Sidebar nav buttons */
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(99,102,241,0.08) !important;
        border: 1px solid rgba(99,102,241,0.12) !important;
        box-shadow: none !important;
        font-size: 0.82rem !important;
        padding: 0.5rem 0.8rem !important;
        text-align: left !important;
        justify-content: flex-start !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(99,102,241,0.18) !important;
        border-color: var(--accent-primary) !important;
        transform: translateX(3px) !important;
    }

    /* ── Metric Cards (Enhanced) ── */
    div[data-testid="stMetric"] {
        background: var(--bg-card) !important;
        backdrop-filter: blur(24px) !important;
        -webkit-backdrop-filter: blur(24px) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: var(--radius) !important;
        padding: 1.3rem 1.5rem !important;
        box-shadow: var(--glass-shadow) !important;
        transition: var(--transition) !important;
        animation: fadeInUp 0.5s ease-out;
    }
    div[data-testid="stMetric"]:hover {
        border-color: var(--accent-primary) !important;
        transform: translateY(-3px) scale(1.01) !important;
        box-shadow: 0 16px 48px rgba(99, 102, 241, 0.12) !important;
    }
    div[data-testid="stMetric"] label {
        color: var(--text-secondary) !important;
        font-size: 0.72rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-weight: 800 !important;
        font-size: 1.5rem !important;
        font-family: 'JetBrains Mono', 'Inter', monospace !important;
    }

    /* ── Primary Buttons ── */
    .stButton > button,
    .stFormSubmitButton > button {
        background: var(--accent-gradient) !important;
        background-size: 200% auto !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.65rem 1.5rem !important;
        transition: var(--transition) !important;
        box-shadow: 0 4px 20px var(--accent-glow) !important;
        position: relative;
        overflow: hidden;
    }
    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px var(--accent-glow) !important;
        background-position: right center !important;
    }
    .stButton > button:active,
    .stFormSubmitButton > button:active {
        transform: translateY(0) !important;
    }

    /* ── Forms & Containers ── */
    div[data-testid="stForm"],
    div[data-testid="stExpander"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: var(--radius) !important;
        backdrop-filter: blur(24px) !important;
        -webkit-backdrop-filter: blur(24px) !important;
        padding: 1.5rem !important;
        animation: fadeInUp 0.4s ease-out;
    }

    /* ── Tabs (Premium) ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px !important;
        background: rgba(10, 10, 20, 0.6) !important;
        border-radius: 14px !important;
        padding: 4px !important;
        border: 1px solid var(--glass-border) !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 11px !important;
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.55rem 1rem !important;
        transition: var(--transition) !important;
        font-size: 0.82rem !important;
    }
    .stTabs [aria-selected="true"] {
        background: var(--accent-gradient) !important;
        color: white !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px var(--accent-glow) !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        background: transparent !important;
        border: none !important;
        padding: 1rem 0 !important;
    }

    /* ── Input Fields (Enhanced) ── */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea textarea {
        background: rgba(10, 10, 20, 0.7) !important;
        border: 1px solid rgba(99, 102, 241, 0.15) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        transition: var(--transition) !important;
        font-size: 0.88rem !important;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea textarea:focus {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12) !important;
    }

    /* Input labels */
    .stTextInput label, .stNumberInput label, .stSelectbox label, .stTextArea label {
        color: var(--text-secondary) !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
    }

    /* ── Select box ── */
    div[data-baseweb="select"] > div {
        background: rgba(10, 10, 20, 0.7) !important;
        border: 1px solid rgba(99, 102, 241, 0.15) !important;
        border-radius: var(--radius-sm) !important;
    }
    div[data-baseweb="popover"] {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 12px !important;
    }
    div[data-baseweb="menu"] { background: var(--bg-secondary) !important; }
    ul[role="listbox"] li { color: var(--text-primary) !important; }
    ul[role="listbox"] li:hover { background: rgba(99, 102, 241, 0.12) !important; }

    /* ── Data Table (Enhanced) ── */
    .stDataFrame {
        border-radius: var(--radius) !important;
        overflow: hidden !important;
        animation: fadeInUp 0.5s ease-out;
    }
    .stDataFrame [data-testid="stDataFrame"] {
        border: 1px solid var(--glass-border) !important;
        border-radius: var(--radius) !important;
    }

    /* ── Bordered Containers ── */
    div[data-testid="stVerticalBlock"] > div[style*="border"] {
        border-color: var(--glass-border) !important;
        border-radius: var(--radius) !important;
        background: var(--bg-card) !important;
        backdrop-filter: blur(24px) !important;
    }

    /* ── Alerts ── */
    .stAlert {
        border-radius: 12px !important;
        backdrop-filter: blur(10px) !important;
        animation: fadeInUp 0.3s ease-out;
    }

    /* ── Divider ── */
    hr { border-color: var(--glass-border) !important; opacity: 0.4 !important; }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        font-size: 0.88rem !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(99, 102, 241, 0.25); border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(99, 102, 241, 0.45); }

    /* ── Plotly ── */
    .js-plotly-plot .plotly .main-svg { border-radius: var(--radius) !important; }

    /* ═══════════════════════════════════════
       CUSTOM HTML COMPONENT STYLES
       ═══════════════════════════════════════ */

    /* ── KPI Cards ── */
    .kpi-card {
        background: var(--bg-card);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius);
        padding: 1.4rem 1.5rem;
        box-shadow: var(--glass-shadow);
        transition: var(--transition);
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.5s ease-out;
    }
    .kpi-card:hover {
        border-color: var(--accent-primary);
        transform: translateY(-4px) scale(1.01);
        box-shadow: 0 16px 48px rgba(99, 102, 241, 0.12);
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: var(--accent-gradient);
        border-radius: var(--radius) var(--radius) 0 0;
    }
    .kpi-card .kpi-label {
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--text-secondary);
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .kpi-card .kpi-value {
        font-size: 1.7rem;
        font-weight: 800;
        color: var(--text-primary);
        line-height: 1.2;
        font-family: 'JetBrains Mono', 'Inter', monospace;
    }
    .kpi-card .kpi-icon {
        font-size: 2rem;
        position: absolute;
        top: 1rem; right: 1.2rem;
        opacity: 0.12;
    }

    /* Colored accent variants */
    .kpi-card.kpi-green::before { background: linear-gradient(135deg, #10b981, #34d399); }
    .kpi-card.kpi-blue::before { background: linear-gradient(135deg, #3b82f6, #60a5fa); }
    .kpi-card.kpi-amber::before { background: linear-gradient(135deg, #f59e0b, #fbbf24); }
    .kpi-card.kpi-red::before { background: linear-gradient(135deg, #ef4444, #f87171); }
    .kpi-card.kpi-purple::before { background: var(--accent-gradient); }

    /* ── Section Headers ── */
    .section-header {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.2rem;
        background: var(--accent-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        letter-spacing: -0.02em;
    }

    /* ── Status Pills ── */
    .status-pill {
        display: inline-block;
        padding: 0.2rem 0.65rem;
        border-radius: 99px;
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-family: 'Inter', sans-serif;
    }
    .pill-green { background: rgba(16,185,129,0.12); color: #10b981; border: 1px solid rgba(16,185,129,0.25); }
    .pill-amber { background: rgba(245,158,11,0.12); color: #f59e0b; border: 1px solid rgba(245,158,11,0.25); }
    .pill-red { background: rgba(239,68,68,0.12); color: #ef4444; border: 1px solid rgba(239,68,68,0.25); }
    .pill-blue { background: rgba(59,130,246,0.12); color: #3b82f6; border: 1px solid rgba(59,130,246,0.25); }
    .pill-purple { background: rgba(139,92,246,0.12); color: #8b5cf6; border: 1px solid rgba(139,92,246,0.25); }

    /* ── Action Cards ── */
    .action-card {
        background: var(--bg-card);
        backdrop-filter: blur(24px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius);
        padding: 1.5rem;
        text-align: center;
        transition: var(--transition);
        cursor: pointer;
        animation: fadeInUp 0.5s ease-out;
    }
    .action-card:hover {
        border-color: var(--accent-primary);
        transform: translateY(-4px);
        box-shadow: 0 16px 48px rgba(99, 102, 241, 0.12);
    }
    .action-card .action-icon { font-size: 2rem; margin-bottom: 0.5rem; }
    .action-card .action-title { font-weight: 600; color: var(--text-primary); font-size: 0.88rem; }
    .action-card .action-desc { font-size: 0.72rem; color: var(--text-secondary); margin-top: 0.25rem; }

    /* ── Page Header ── */
    .page-header {
        background: linear-gradient(135deg, rgba(99,102,241,0.08), rgba(139,92,246,0.04), rgba(59,130,246,0.03));
        border: 1px solid var(--glass-border);
        border-radius: var(--radius);
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        animation: fadeInUp 0.4s ease-out;
        position: relative;
        overflow: hidden;
    }
    .page-header::after {
        content: '';
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 2px;
        background: var(--accent-gradient);
    }
    .page-header h1 { margin: 0 !important; padding: 0 !important; font-size: 1.6rem !important; }
    .page-header .page-subtitle { color: var(--text-secondary); font-size: 0.85rem; margin-top: 0.3rem; }

    /* ── Stat Grid ── */
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-bottom: 1.5rem;
    }

    /* ── Info Badge ── */
    .info-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(59,130,246,0.1);
        border: 1px solid rgba(59,130,246,0.2);
        border-radius: 99px;
        padding: 0.3rem 0.8rem;
        font-size: 0.72rem;
        color: #60a5fa;
        font-weight: 500;
    }

    /* ── Empty state ── */
    .empty-state {
        text-align: center;
        padding: 3rem 1rem;
        color: var(--text-secondary);
    }
    .empty-state .empty-icon { font-size: 3.5rem; margin-bottom: 0.8rem; opacity: 0.5; animation: float 3s ease-in-out infinite; }
    .empty-state .empty-title { font-size: 1rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.3rem; }
    .empty-state .empty-desc { font-size: 0.82rem; }
    </style>
    """, unsafe_allow_html=True)


# ────────────────────────────────────────────
#  HTML Component Helpers
# ────────────────────────────────────────────
def kpi_card(label: str, value: str, icon: str = "📊", color: str = "purple"):
    """Return an HTML KPI card with colored accent. color: purple|green|blue|amber|red"""
    return f"""
    <div class="kpi-card kpi-{color}">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """


def page_header(title: str, subtitle: str = "", icon: str = ""):
    """Render a premium page header with gradient accent bar."""
    st.markdown(f"""
    <div class="page-header">
        <h1>{icon} {title}</h1>
        <div class="page-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def empty_state(icon: str, title: str, description: str):
    """Render a styled empty state placeholder."""
    st.markdown(f"""
    <div class="empty-state">
        <div class="empty-icon">{icon}</div>
        <div class="empty-title">{title}</div>
        <div class="empty-desc">{description}</div>
    </div>
    """, unsafe_allow_html=True)


def status_pill(text: str, color: str = "blue"):
    """Return an HTML status pill. color: green|amber|red|blue|purple"""
    return f'<span class="status-pill pill-{color}">{text}</span>'


def render_notification():
    """Renders a premium custom toast notification if one exists in session state."""
    if "toast_msg" in st.session_state and st.session_state.toast_msg:
        st.markdown(f"""
        <div style="
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 999999;
            background: rgba(16, 185, 129, 0.15);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(16, 185, 129, 0.4);
            border-radius: 12px;
            padding: 16px 24px;
            color: #fff;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            box-shadow: 0 10px 40px -10px rgba(16, 185, 129, 0.3), 0 0 15px rgba(16, 185, 129, 0.2);
            display: flex;
            align-items: center;
            gap: 12px;
            animation: slideDownFadeOut 4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        ">
            <div style="
                background: linear-gradient(135deg, #10b981, #059669);
                border-radius: 50%;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
            ">✓</div>
            <div style="font-size: 0.95rem; letter-spacing: 0.01em;">
                {st.session_state.toast_msg}
            </div>
        </div>
        <style>
        @keyframes slideDownFadeOut {{
            0% {{ top: -50px; opacity: 0; transform: translateX(-50%) scale(0.95); }}
            10% {{ top: 20px; opacity: 1; transform: translateX(-50%) scale(1); }}
            85% {{ top: 20px; opacity: 1; transform: translateX(-50%) scale(1); }}
            100% {{ top: -20px; opacity: 0; transform: translateX(-50%) scale(0.95); }}
        }}
        </style>
        """, unsafe_allow_html=True)
        # Clear it so it doesn't show again on next interaction
        del st.session_state.toast_msg

