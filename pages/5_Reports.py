import streamlit as st
import plotly.graph_objects as go
from nexus_commerce.reports import logic as report_logic
from nexus_commerce.inventory import logic as inv_logic
from nexus_commerce.expenses import logic as expense_logic
from nexus_commerce.common._utils import inject_custom_css, render_sidebar, page_header, kpi_card

# ── Page Config ──
st.set_page_config(page_title="Reports | Nexus Commerce", layout="wide", page_icon="📈")
if not st.session_state.get("authenticated"):
    st.error("🔒 You must be logged in."); st.stop()

inject_custom_css()
render_sidebar()

page_header("Business Intelligence Reports", "Revenue, profit, product health, payment analysis & discount simulation", "📈")

tab_rev, tab_health, tab_payment, tab_sim = st.tabs([
    "💰 **Revenue & Profit**",
    "🏥 **Product Health**",
    "💳 **Payment Analysis**",
    "🧮 **Sale Simulator**"
])

# ── REVENUE & PROFIT ──
with tab_rev:
    period = st.selectbox("Report Period", ['daily', 'weekly', 'monthly'],
                          format_func=lambda x: {"daily": "📅 Last 24 Hours", "weekly": "📅 Last 7 Days", "monthly": "📅 Last 30 Days"}[x],
                          key="rev_period")

    with st.spinner("Loading report…"):
        data = report_logic.get_profit_report(period)
        days = 1 if period == 'daily' else 7 if period == 'weekly' else 30
        expense_data = expense_logic.get_expense_summary(days)

    if data.get("error"):
        st.error(data['error'], icon="🚨")
    else:
        revenue = data.get('total_revenue', 0)
        gross_profit = data.get('total_profit', 0)
        expenses = expense_data.get('total', 0)
        net_profit = gross_profit - expenses
        margin = (net_profit / revenue * 100) if revenue > 0 else 0

        r1, r2, r3, r4 = st.columns(4)
        with r1: st.markdown(kpi_card("Total Revenue", f"₹{revenue:,.2f}", "💰", "green"), unsafe_allow_html=True)
        with r2: st.markdown(kpi_card("Gross Profit", f"₹{gross_profit:,.2f}", "📈", "blue"), unsafe_allow_html=True)
        with r3: st.markdown(kpi_card("Overhead Expenses", f"₹{expenses:,.2f}", "💸", "red"), unsafe_allow_html=True)
        with r4: st.markdown(kpi_card("Net Profit", f"₹{net_profit:,.2f}", "🎯", "purple"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Donut chart
        fig = go.Figure(data=[go.Pie(
            labels=['Gross Profit', 'Cost & Overhead'],
            values=[gross_profit, max(0, revenue - gross_profit)],
            hole=0.65,
            marker=dict(colors=['#10b981', 'rgba(239,68,68,0.6)'],
                        line=dict(color='rgba(0,0,0,0.3)', width=2)),
            textinfo='label+percent',
            textfont=dict(size=12, color='rgba(226,232,240,0.8)'),
            hovertemplate='<b>%{label}</b><br>₹%{value:,.2f}<br>%{percent}<extra></extra>'
        )])
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='rgba(226,232,240,0.6)'),
            margin=dict(l=20, r=20, t=20, b=20), height=320,
            legend=dict(font=dict(size=11)),
            annotations=[dict(text=f"<b>₹{revenue:,.0f}</b>", x=0.5, y=0.5, font_size=16,
                              font_color='rgba(226,232,240,0.8)', showarrow=False)]
        )
        st.plotly_chart(fig, use_container_width=True)

# ── PRODUCT HEALTH ──
with tab_health:
    with st.spinner("Analyzing products…"):
        health = report_logic.get_product_health_report()

    if health.get("error"):
        st.error(health['error'], icon="🚨")
    else:
        products = health.get('data', [])
        hot = sum(1 for p in products if p['status'] == 'Hot')
        cooling = sum(1 for p in products if p['status'] == 'Cooling')
        frozen = sum(1 for p in products if p['status'] == 'Frozen')

        h1, h2, h3 = st.columns(3)
        with h1: st.markdown(kpi_card("Hot (< 30 days)", str(hot), "🔥", "green"), unsafe_allow_html=True)
        with h2: st.markdown(kpi_card("Cooling (30-90 days)", str(cooling), "❄️", "amber"), unsafe_allow_html=True)
        with h3: st.markdown(kpi_card("Frozen (> 90 days)", str(frozen), "🥶", "red"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if products:
            fig = go.Figure(data=[go.Pie(
                labels=['Hot', 'Cooling', 'Frozen'],
                values=[hot, cooling, frozen],
                marker=dict(colors=['#10b981', '#f59e0b', '#ef4444'],
                            line=dict(color='rgba(0,0,0,0.3)', width=2)),
                textinfo='label+value+percent',
                textfont=dict(size=11, color='white'),
                hovertemplate='<b>%{label}</b><br>%{value} products<br>%{percent}<extra></extra>'
            )])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter', color='rgba(226,232,240,0.6)'),
                margin=dict(l=20, r=20, t=20, b=20), height=280,
                legend=dict(font=dict(size=11))
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-header">Detailed Breakdown</div>', unsafe_allow_html=True)
            
            # Product list cards
            for p in products:
                color = "green" if p['status'] == 'Hot' else 'amber' if p['status'] == 'Cooling' else 'red'
                st.markdown(f"""
                <div style="
                    background: var(--bg-card); 
                    border: 1px solid var(--glass-border); 
                    border-radius: 10px; 
                    padding: 12px 18px; 
                    margin-bottom: 10px; 
                    display: flex; 
                    justify-content: space-between; 
                    align-items: center;
                    transition: var(--transition-fast);
                " onmouseover="this.style.borderColor='var(--accent-primary)';" onmouseout="this.style.borderColor='var(--glass-border)';">
                    <div>
                        <strong style="color: var(--text-primary); font-size: 1.05rem;">{p['name']}</strong>
                        <span style="color: var(--text-secondary); background: rgba(255,255,255,0.05); padding: 2px 6px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; margin-left: 10px;">{p['sku']}</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 20px;">
                        <span style="color: var(--text-secondary); font-size: 0.9rem;">Stock: <strong style="color: var(--text-primary);">{p['quantity']}</strong> units</span>
                        <span class="status-pill pill-{color}" style="min-width: 90px; text-align: center; font-weight: 600;">{p['status']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ── PAYMENT ANALYSIS ──
with tab_payment:
    pay_period = st.selectbox("Period", ['daily', 'weekly', 'monthly'],
                              format_func=lambda x: {"daily": "📅 Last 24 Hours", "weekly": "📅 Last 7 Days", "monthly": "📅 Last 30 Days"}[x],
                              key="pay_period")

    with st.spinner("Loading payments…"):
        payments = report_logic.get_payment_summary(pay_period)

    if payments.get("error"):
        st.error(payments['error'], icon="🚨")
    else:
        summary = payments.get('summary', {})
        if not summary:
            st.info("No payment data for this period.", icon="💳")
        else:
            cols = st.columns(len(summary))
            colors = {"Cash": "green", "Card": "blue", "UPI": "purple", "Bank Transfer": "amber"}
            for i, (method, amount) in enumerate(summary.items()):
                with cols[i]:
                    st.markdown(kpi_card(method, f"₹{amount:,.2f}", "💳", colors.get(method, "blue")), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            fig = go.Figure(data=[go.Pie(
                labels=list(summary.keys()),
                values=list(summary.values()),
                hole=0.5,
                marker=dict(colors=['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b'][:len(summary)],
                            line=dict(color='rgba(0,0,0,0.3)', width=2)),
                textinfo='label+percent',
                textfont=dict(size=11, color='rgba(226,232,240,0.8)'),
                hovertemplate='<b>%{label}</b><br>₹%{value:,.2f}<br>%{percent}<extra></extra>'
            )])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter', color='rgba(226,232,240,0.6)'),
                margin=dict(l=20, r=20, t=20, b=20), height=300,
                legend=dict(font=dict(size=11))
            )
            st.plotly_chart(fig, use_container_width=True)

# ── SALE SIMULATOR ──
with tab_sim:
    st.markdown('<div class="section-header">Discount Impact Simulator</div>', unsafe_allow_html=True)
    st.caption("Simulate the financial impact of a discount across selected products.")

    products_data = inv_logic.get_all_products()
    product_list = products_data if isinstance(products_data, list) else []

    if not product_list:
        st.info("No products in inventory to simulate.", icon="📦")
    else:
        discount = st.slider("Discount Percentage", 0.0, 75.0, 10.0, 0.5, format="%.1f%%")

        all_skus = [p['sku'] for p in product_list]
        selected_skus = st.multiselect("Select Products (SKUs)", all_skus, default=all_skus[:5] if len(all_skus) >= 5 else all_skus)

        if selected_skus and st.button("🧮 Run Simulation", use_container_width=True, type="primary"):
            with st.spinner("Simulating…"):
                result = report_logic.simulate_sale(discount, selected_skus)

            sim_data = result.get('data', [])
            if sim_data:
                total_original = sum(s.get('original_profit', 0) for s in sim_data if 'name' in s)
                total_new = sum(s.get('new_profit', 0) for s in sim_data if 'name' in s)
                impact = total_new - total_original
                loss_products = sum(1 for s in sim_data if s.get('new_profit', 0) < 0)

                s1, s2, s3 = st.columns(3)
                with s1: st.markdown(kpi_card("Original Profit/Unit", f"₹{total_original:,.2f}", "💰", "green"), unsafe_allow_html=True)
                with s2: st.markdown(kpi_card(f"After {discount}% Discount", f"₹{total_new:,.2f}", "💸", "amber" if total_new > 0 else "red"), unsafe_allow_html=True)
                with s3: st.markdown(kpi_card("Impact", f"₹{impact:,.2f}", "📊", "red" if impact < 0 else "green"), unsafe_allow_html=True)

                if loss_products > 0:
                    st.error(f"⚠️ Warning: {loss_products} product(s) would operate at a **loss** with this discount!", icon="🚨")

                st.markdown("<br>", unsafe_allow_html=True)

                # Bar chart comparison
                names = [s['name'][:20] for s in sim_data if 'name' in s]
                orig = [s['original_profit'] for s in sim_data if 'name' in s]
                new = [s['new_profit'] for s in sim_data if 'name' in s]

                fig = go.Figure(data=[
                    go.Bar(name='Original Profit', x=names, y=orig,
                           marker=dict(color='#6366f1', line=dict(width=0)),
                           hovertemplate='<b>%{x}</b><br>₹%{y:,.2f}<extra>Original</extra>'),
                    go.Bar(name=f'After {discount}% Off', x=names, y=new,
                           marker=dict(color=['#10b981' if v >= 0 else '#ef4444' for v in new], line=dict(width=0)),
                           hovertemplate='<b>%{x}</b><br>₹%{y:,.2f}<extra>After Discount</extra>')
                ])
                fig.update_layout(
                    barmode='group',
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family='Inter', color='rgba(226,232,240,0.6)', size=11),
                    xaxis=dict(gridcolor='rgba(99,102,241,0.06)', showline=False),
                    yaxis=dict(gridcolor='rgba(99,102,241,0.06)', showline=False, title="Profit per Unit (₹)"),
                    margin=dict(l=10, r=10, t=30, b=10), height=350,
                    legend=dict(font=dict(size=11))
                )
                fig.add_hline(y=0, line_dash="dash", line_color="rgba(239,68,68,0.5)")
                st.plotly_chart(fig, use_container_width=True)
