import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from nexus_commerce.analytics import logic as analytics_logic
from nexus_commerce.common._utils import inject_custom_css, render_sidebar, page_header, kpi_card, status_pill

# ── Page Config ──
st.set_page_config(page_title="Analytics | Nexus Commerce", layout="wide", page_icon="🔬")
if not st.session_state.get("authenticated"):
    st.error("🔒 You must be logged in."); st.stop()

inject_custom_css()
render_sidebar()

page_header("Advanced Analytics", "Data Science-powered insights — ABC Analysis, Forecasting, Correlation, RFM Segmentation", "🔬")

tab_abc, tab_forecast, tab_corr, tab_rfm, tab_ma = st.tabs([
    "📊 **ABC Analysis**",
    "🔮 **Sales Forecast**",
    "🔗 **Correlation Matrix**",
    "👥 **RFM Segmentation**",
    "📈 **Moving Averages**"
])

# ═══════════════════════════════════════
#  ABC ANALYSIS (Pareto / 80-20 Rule)
# ═══════════════════════════════════════
with tab_abc:
    st.markdown('<div class="section-header">📊 ABC Analysis — Pareto Classification</div>', unsafe_allow_html=True)
    st.caption("Classifies products by revenue contribution: **A** (top 80%), **B** (next 15%), **C** (remaining 5%). Based on the Pareto (80/20) principle.")

    if st.button("Run ABC Analysis", type="primary", use_container_width=True, key="run_abc"):
        with st.spinner("Running ABC classification…"):
            result = analytics_logic.get_abc_analysis()

        if result.get("error"):
            st.error(result['error'], icon="🚨")
        elif not result.get("data"):
            st.info("Not enough sales data. Record some sales first.", icon="📊")
        else:
            summary = result['summary']
            data = result['data']

            # KPIs
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.markdown(kpi_card("Category A", str(summary['A']), "🏆", "green"), unsafe_allow_html=True)
            with c2: st.markdown(kpi_card("Category B", str(summary['B']), "📦", "amber"), unsafe_allow_html=True)
            with c3: st.markdown(kpi_card("Category C", str(summary['C']), "📉", "red"), unsafe_allow_html=True)
            with c4: st.markdown(kpi_card("Total Revenue", f"₹{summary['total_revenue']:,.0f}", "💰", "purple"), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Pareto chart
            df = pd.DataFrame(data)
            fig = go.Figure()
            colors = ['#10b981' if c == 'A' else '#f59e0b' if c == 'B' else '#ef4444' for c in df['category']]
            fig.add_trace(go.Bar(
                x=df['product_name'], y=df['total_revenue'],
                marker=dict(color=colors, line=dict(width=0)),
                name='Revenue',
                hovertemplate='<b>%{x}</b><br>₹%{y:,.2f}<extra></extra>'
            ))
            fig.add_trace(go.Scatter(
                x=df['product_name'], y=df['cumulative_pct'],
                yaxis='y2', mode='lines+markers',
                line=dict(color='#a78bfa', width=2.5),
                marker=dict(size=6, color='#8b5cf6'),
                name='Cumulative %',
                hovertemplate='%{y:.1f}%<extra></extra>'
            ))
            fig.add_hline(y=80, line_dash="dash", line_color="rgba(16,185,129,0.4)", yref='y2',
                          annotation_text="80% threshold", annotation_font_color="rgba(16,185,129,0.6)")
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter', color='rgba(226,232,240,0.6)', size=11),
                xaxis=dict(gridcolor='rgba(99,102,241,0.06)', showline=False, title=None),
                yaxis=dict(gridcolor='rgba(99,102,241,0.06)', showline=False, title="Revenue (₹)"),
                yaxis2=dict(title="Cumulative %", overlaying='y', side='right', range=[0, 105],
                            gridcolor='rgba(0,0,0,0)'),
                margin=dict(l=10, r=10, t=30, b=10), height=380,
                legend=dict(font=dict(size=11)), barmode='relative'
            )
            st.plotly_chart(fig, use_container_width=True)

            # Data table
            st.markdown("<br>", unsafe_allow_html=True)
            for item in data:
                color = "green" if item['category'] == 'A' else 'amber' if item['category'] == 'B' else 'red'
                st.markdown(
                    f"{status_pill(item['category'], color)} "
                    f"**{item['product_name']}** `{item['product_sku']}` — "
                    f"₹{item['total_revenue']:,.2f} ({item['revenue_pct']:.1f}%) — "
                    f"{item['total_units']} units sold",
                    unsafe_allow_html=True
                )

# ═══════════════════════════════════════
#  SALES FORECASTING (Linear Regression)
# ═══════════════════════════════════════
with tab_forecast:
    st.markdown('<div class="section-header">🔮 Sales Forecast — Linear Regression</div>', unsafe_allow_html=True)
    st.caption("Uses historical sales data to project future revenue using **numpy's polyfit** with 95% confidence intervals.")

    fc1, fc2 = st.columns(2)
    with fc1: history_days = st.slider("Historical Data (Days)", 7, 90, 30, key="fc_history")
    with fc2: forecast_days = st.slider("Forecast Horizon (Days)", 3, 30, 7, key="fc_forecast")

    if st.button("🔮 Generate Forecast", type="primary", use_container_width=True, key="run_forecast"):
        with st.spinner("Running linear regression…"):
            result = analytics_logic.get_sales_forecast(history_days, forecast_days)

        if result.get("error"):
            st.info(result['error'], icon="📊")
        else:
            # KPIs
            k1, k2, k3, k4 = st.columns(4)
            trend_icon = "📈" if result['trend'] == 'upward' else "📉" if result['trend'] == 'downward' else "➡️"
            trend_color = "green" if result['trend'] == 'upward' else "red" if result['trend'] == 'downward' else "blue"
            with k1: st.markdown(kpi_card("Trend", result['trend'].capitalize(), trend_icon, trend_color), unsafe_allow_html=True)
            with k2: st.markdown(kpi_card("Daily Growth", f"₹{result['daily_growth']:,.2f}", "📊", "blue"), unsafe_allow_html=True)
            with k3: st.markdown(kpi_card("R² Score", f"{result['r_squared']:.4f}", "🎯", "purple"), unsafe_allow_html=True)
            with k4: st.markdown(kpi_card("Std Error", f"₹{result['std_error']:,.2f}", "📏", "amber"), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Chart
            hist = result['historical']
            fcast = result['forecast']

            fig = go.Figure()

            # Historical
            fig.add_trace(go.Scatter(
                x=[h['date'] for h in hist], y=[h['revenue'] for h in hist],
                fill='tozeroy', fillcolor='rgba(99,102,241,0.08)',
                line=dict(color='#6366f1', width=2, shape='spline'),
                mode='lines+markers',
                marker=dict(size=4, color='#8b5cf6'),
                name='Historical',
                hovertemplate='<b>%{x}</b><br>₹%{y:,.2f}<extra>Historical</extra>'
            ))

            # Forecast
            fig.add_trace(go.Scatter(
                x=[f['date'] for f in fcast], y=[f['revenue'] for f in fcast],
                line=dict(color='#10b981', width=2.5, dash='dot'),
                mode='lines+markers',
                marker=dict(size=6, color='#10b981', symbol='diamond'),
                name='Forecast',
                hovertemplate='<b>%{x}</b><br>₹%{y:,.2f}<extra>Forecast</extra>'
            ))

            # Confidence interval
            fig.add_trace(go.Scatter(
                x=[f['date'] for f in fcast] + [f['date'] for f in fcast][::-1],
                y=[f['upper'] for f in fcast] + [f['lower'] for f in fcast][::-1],
                fill='toself', fillcolor='rgba(16,185,129,0.08)',
                line=dict(color='rgba(0,0,0,0)'),
                name='95% Confidence',
                hoverinfo='skip'
            ))

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter', color='rgba(226,232,240,0.6)', size=11),
                xaxis=dict(gridcolor='rgba(99,102,241,0.06)', showline=False, title=None),
                yaxis=dict(gridcolor='rgba(99,102,241,0.06)', showline=False, title="Revenue (₹)"),
                margin=dict(l=10, r=10, t=10, b=10), height=380,
                legend=dict(font=dict(size=11)), hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════
#  CORRELATION MATRIX (Pearson)
# ═══════════════════════════════════════
with tab_corr:
    st.markdown('<div class="section-header">🔗 Correlation Analysis — Pearson Coefficient</div>', unsafe_allow_html=True)
    st.caption("Analyzes relationships between product attributes (price, stock, margin) and sales performance.")

    if st.button("🔗 Run Correlation Analysis", type="primary", use_container_width=True, key="run_corr"):
        with st.spinner("Computing correlation matrix…"):
            result = analytics_logic.get_correlation_analysis()

        if result.get("error"):
            st.info(result['error'], icon="📊")
        else:
            columns = result['columns']
            matrix = result['matrix']

            # Create numpy-style matrix for heatmap
            z = [[matrix[col1][col2] for col2 in columns] for col1 in columns]
            labels = [c.replace('_', ' ').title() for c in columns]

            fig = go.Figure(data=go.Heatmap(
                z=z, x=labels, y=labels,
                colorscale=[[0, '#ef4444'], [0.5, '#0a0a14'], [1, '#10b981']],
                zmid=0, zmin=-1, zmax=1,
                text=[[f"{v:.3f}" for v in row] for row in z],
                texttemplate="%{text}",
                textfont=dict(size=11, color='rgba(226,232,240,0.8)'),
                hovertemplate='<b>%{x} vs %{y}</b><br>Correlation: %{z:.3f}<extra></extra>'
            ))
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter', color='rgba(226,232,240,0.6)', size=11),
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=False, autorange='reversed'),
                margin=dict(l=10, r=10, t=10, b=10), height=420
            )
            st.plotly_chart(fig, use_container_width=True)

            # Auto-generated insights
            insights = result.get('insights', [])
            if insights:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="section-header">💡 Key Insights</div>', unsafe_allow_html=True)
                for insight in insights:
                    st.markdown(f"• {insight}")

# ═══════════════════════════════════════
#  RFM SEGMENTATION (Customer DS)
# ═══════════════════════════════════════
with tab_rfm:
    st.markdown('<div class="section-header">👥 RFM Customer Segmentation</div>', unsafe_allow_html=True)
    st.caption("Segments customers by **Recency** (last purchase), **Frequency** (number of purchases), and **Monetary** (total spent) into Gold/Silver/Bronze tiers.")

    if st.button("👥 Run RFM Analysis", type="primary", use_container_width=True, key="run_rfm"):
        with st.spinner("Segmenting customers…"):
            result = analytics_logic.get_rfm_analysis()

        if result.get("error"):
            st.info(result['error'], icon="📊")
        else:
            summary = result['summary']
            data = result['data']

            # KPIs
            k1, k2, k3 = st.columns(3)
            with k1: st.markdown(kpi_card("🥇 Gold", str(summary['Gold']), "⭐", "amber"), unsafe_allow_html=True)
            with k2: st.markdown(kpi_card("🥈 Silver", str(summary['Silver']), "🔘", "blue"), unsafe_allow_html=True)
            with k3: st.markdown(kpi_card("🥉 Bronze", str(summary['Bronze']), "📦", "red"), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Segment distribution pie
            fig = go.Figure(data=[go.Pie(
                labels=['Gold', 'Silver', 'Bronze'],
                values=[summary['Gold'], summary['Silver'], summary['Bronze']],
                marker=dict(colors=['#f59e0b', '#3b82f6', '#ef4444'],
                            line=dict(color='rgba(0,0,0,0.3)', width=2)),
                textinfo='label+value+percent',
                textfont=dict(size=12, color='white'),
                hole=0.55,
                hovertemplate='<b>%{label}</b><br>%{value} customers<br>%{percent}<extra></extra>'
            )])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter', color='rgba(226,232,240,0.6)'),
                margin=dict(l=20, r=20, t=20, b=20), height=280,
                legend=dict(font=dict(size=11))
            )
            st.plotly_chart(fig, use_container_width=True)

            # Customer table
            st.markdown("<br>", unsafe_allow_html=True)
            for c in data:
                color = "amber" if c['segment'] == 'Gold' else 'blue' if c['segment'] == 'Silver' else 'red'
                st.markdown(
                    f"{status_pill(c['segment'], color)} "
                    f"**{c['customer_name']}** ({c['customer_phone']}) — "
                    f"Score: {c['rfm_score']} | "
                    f"Recency: {c['recency']}d | Frequency: {c['frequency']} | "
                    f"₹{c['monetary']:,.2f}",
                    unsafe_allow_html=True
                )

# ═══════════════════════════════════════
#  MOVING AVERAGES (Trend Smoothing)
# ═══════════════════════════════════════
with tab_ma:
    st.markdown('<div class="section-header">📈 Moving Averages — Trend Smoothing</div>', unsafe_allow_html=True)
    st.caption("Overlays **7-day** and **30-day** moving averages on daily sales to identify underlying trends and filter noise.")

    ma_days = st.slider("Data Window (Days)", 30, 180, 90, key="ma_days")

    if st.button("📈 Calculate Moving Averages", type="primary", use_container_width=True, key="run_ma"):
        with st.spinner("Computing moving averages…"):
            result = analytics_logic.get_moving_averages(ma_days)

        if result.get("error"):
            st.info(result['error'], icon="📊")
        else:
            data = result['data']

            fig = go.Figure()

            # Daily revenue (subtle bars)
            fig.add_trace(go.Bar(
                x=[d['date'] for d in data], y=[d['revenue'] for d in data],
                marker=dict(color='rgba(99,102,241,0.15)', line=dict(width=0)),
                name='Daily Revenue',
                hovertemplate='<b>%{x}</b><br>₹%{y:,.2f}<extra>Daily</extra>'
            ))

            # 7-day MA
            fig.add_trace(go.Scatter(
                x=[d['date'] for d in data], y=[d['ma_7'] for d in data],
                line=dict(color='#10b981', width=2.5, shape='spline'),
                name='7-Day MA',
                hovertemplate='₹%{y:,.2f}<extra>7-Day MA</extra>'
            ))

            # 30-day MA
            fig.add_trace(go.Scatter(
                x=[d['date'] for d in data], y=[d['ma_30'] for d in data],
                line=dict(color='#f59e0b', width=2.5, shape='spline'),
                name='30-Day MA',
                hovertemplate='₹%{y:,.2f}<extra>30-Day MA</extra>'
            ))

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter', color='rgba(226,232,240,0.6)', size=11),
                xaxis=dict(gridcolor='rgba(99,102,241,0.06)', showline=False, title=None),
                yaxis=dict(gridcolor='rgba(99,102,241,0.06)', showline=False, title="Revenue (₹)"),
                margin=dict(l=10, r=10, t=10, b=10), height=400,
                legend=dict(font=dict(size=11)), hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)

            # Summary stats
            if data:
                latest = data[-1]
                st.markdown("<br>", unsafe_allow_html=True)
                s1, s2, s3 = st.columns(3)
                with s1: st.markdown(kpi_card("Latest Daily", f"₹{latest['revenue']:,.2f}", "📊", "blue"), unsafe_allow_html=True)
                with s2: st.markdown(kpi_card("7-Day MA", f"₹{latest['ma_7']:,.2f}", "📈", "green"), unsafe_allow_html=True)
                with s3: st.markdown(kpi_card("30-Day MA", f"₹{latest['ma_30']:,.2f}", "📉", "amber"), unsafe_allow_html=True)
