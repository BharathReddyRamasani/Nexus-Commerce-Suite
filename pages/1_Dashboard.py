import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from nexus_commerce.inventory import logic as inventory_logic
from nexus_commerce.customers import logic as customer_logic
from nexus_commerce.reports import logic as report_logic
from nexus_commerce.common._utils import inject_custom_css, render_sidebar, page_header, kpi_card

# ── Page Config ──
st.set_page_config(page_title="Dashboard | Nexus Commerce", layout="wide", page_icon="📊")
if not st.session_state.get("authenticated"):
    st.error("🔒 You must be logged in."); st.stop()

inject_custom_css()
render_sidebar()

page_header("Executive Dashboard", f"Real-time business intelligence — {datetime.now().strftime('%d %b %Y, %I:%M %p')}", "📊")

# ── KPIs ──
with st.spinner("Loading metrics…"):
    products = inventory_logic.get_all_products()
    customers = customer_logic.get_all_customers()
    daily = report_logic.get_profit_report('daily')
    weekly = report_logic.get_profit_report('weekly')
    inv_summary = inventory_logic.get_inventory_summary()

    tp = len(products) if isinstance(products, list) else 0
    tc = len(customers) if isinstance(customers, list) else 0
    dr = daily.get('total_revenue', 0)
    dp = daily.get('total_profit', 0)
    wr = weekly.get('total_revenue', 0)

c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.markdown(kpi_card("Total Products", str(tp), "📦", "blue"), unsafe_allow_html=True)
with c2: st.markdown(kpi_card("Total Customers", str(tc), "👥", "purple"), unsafe_allow_html=True)
with c3: st.markdown(kpi_card("Revenue (24h)", f"₹{dr:,.0f}", "💰", "green"), unsafe_allow_html=True)
with c4: st.markdown(kpi_card("Profit (24h)", f"₹{dp:,.0f}", "📈", "amber"), unsafe_allow_html=True)
with c5: st.markdown(kpi_card("Revenue (7d)", f"₹{wr:,.0f}", "💎", "purple"), unsafe_allow_html=True)

# ── Inventory Value ──
st.markdown("<br>", unsafe_allow_html=True)
if not inv_summary.get("error"):
    iv1, iv2, iv3 = st.columns(3)
    with iv1: st.markdown(kpi_card("Stock Value (Cost)", f"₹{inv_summary['total_cost_value']:,.0f}", "🏷️", "blue"), unsafe_allow_html=True)
    with iv2: st.markdown(kpi_card("Stock Value (Retail)", f"₹{inv_summary['total_sell_value']:,.0f}", "💳", "green"), unsafe_allow_html=True)
    with iv3: st.markdown(kpi_card("Potential Profit", f"₹{inv_summary['potential_profit']:,.0f}", "🎯", "amber"), unsafe_allow_html=True)

# ── Sales Trend ──
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-header">📈 Sales Trend Analysis</div>', unsafe_allow_html=True)

time_window = st.selectbox("Time Window", (7, 30, 90), format_func=lambda x: f"Last {x} Days", index=1)

with st.spinner("Loading chart…"):
    sales_response = report_logic.get_sales_over_time(time_window)
    if "error" in sales_response:
        st.error(sales_response['error'], icon="🚨")
    else:
        sales_data = sales_response.get("data", [])
        if not sales_data:
            st.info(f"No sales data for the last {time_window} days.", icon="📊")
        else:
            df = pd.DataFrame(sales_data)
            df['sale_date'] = pd.to_datetime(df['sale_date']).dt.date
            daily_sales = df.groupby('sale_date')['total_amount'].sum().reset_index()
            daily_sales.columns = ['Date', 'Revenue']

            tr = daily_sales['Revenue'].sum()
            best = daily_sales['Revenue'].max()
            best_d = daily_sales.loc[daily_sales['Revenue'].idxmax(), 'Date'].strftime('%d %b') if not daily_sales.empty else "N/A"
            avg_daily = daily_sales['Revenue'].mean()

            m1, m2, m3 = st.columns(3)
            with m1: st.markdown(kpi_card(f"Period Revenue", f"₹{tr:,.0f}", "💎", "green"), unsafe_allow_html=True)
            with m2: st.markdown(kpi_card(f"Best Day ({best_d})", f"₹{best:,.0f}", "🏆", "amber"), unsafe_allow_html=True)
            with m3: st.markdown(kpi_card(f"Avg Daily", f"₹{avg_daily:,.0f}", "📊", "blue"), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily_sales['Date'], y=daily_sales['Revenue'],
                fill='tozeroy', fillcolor='rgba(99, 102, 241, 0.12)',
                line=dict(color='#6366f1', width=2.5, shape='spline'),
                mode='lines+markers',
                marker=dict(size=5, color='#8b5cf6', line=dict(width=1, color='#a78bfa')),
                name='Revenue',
                hovertemplate='<b>%{x|%d %b %Y}</b><br>₹%{y:,.2f}<extra></extra>'
            ))
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter', color='rgba(226,232,240,0.6)', size=11),
                xaxis=dict(gridcolor='rgba(99,102,241,0.06)', showline=False, title=None),
                yaxis=dict(gridcolor='rgba(99,102,241,0.06)', showline=False, title="Revenue (₹)", title_font_size=11),
                margin=dict(l=10, r=10, t=10, b=10), height=320, hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)

# ── Top Products ──
if isinstance(products, list) and products:
    st.markdown('<div class="section-header">🏅 Top Products by Selling Price</div>', unsafe_allow_html=True)
    pdf = pd.DataFrame(products).nlargest(5, 'selling_price')
    fig2 = go.Figure(go.Bar(
        y=pdf['name'], x=pdf['selling_price'],
        orientation='h',
        marker=dict(
            color=pdf['selling_price'],
            colorscale=[[0, '#6366f1'], [1, '#a78bfa']],
            line=dict(width=0)
        ),
        text=[f"₹{p:,.0f}" for p in pdf['selling_price']],
        textposition='outside', textfont=dict(size=11, color='rgba(226,232,240,0.7)'),
        hovertemplate='<b>%{y}</b><br>₹%{x:,.2f}<extra></extra>'
    ))
    fig2.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='rgba(226,232,240,0.6)', size=11),
        xaxis=dict(gridcolor='rgba(99,102,241,0.06)', showline=False, title=None),
        yaxis=dict(showline=False, title=None, autorange='reversed'),
        margin=dict(l=10, r=60, t=10, b=10), height=220
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Quick Actions ──
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-header">⚡ Quick Actions</div>', unsafe_allow_html=True)

q1, q2, q3, q4, q5 = st.columns(5)
actions = [
    (q1, "📦", "Inventory", "Manage stock", "pages/2_Inventory_Management.py"),
    (q2, "🛒", "New Sale", "POS terminal", "pages/3_Record_Sale.py"),
    (q3, "👥", "Customers", "CRM portal", "pages/4_Customer_Management.py"),
    (q4, "📊", "Reports", "BI insights", "pages/5_Reports.py"),
    (q5, "🔬", "Analytics", "Data science", "pages/6_Analytics.py"),
]
for col, icon, title, desc, page in actions:
    with col:
        st.markdown(f"""
        <div class="action-card">
            <div class="action-icon">{icon}</div>
            <div class="action-title">{title}</div>
            <div class="action-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"{icon} {title}", use_container_width=True, key=f"qa_{title}"):
            st.switch_page(page)
