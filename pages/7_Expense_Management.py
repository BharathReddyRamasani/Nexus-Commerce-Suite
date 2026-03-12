import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from nexus_commerce.expenses import logic as expense_logic
from nexus_commerce.common._utils import inject_custom_css, render_sidebar, page_header, kpi_card, status_pill

# ── Page Config ──
st.set_page_config(page_title="Expenses | Nexus Commerce", layout="wide", page_icon="💸")
if not st.session_state.get("authenticated"):
    st.error("🔒 You must be logged in."); st.stop()

inject_custom_css()
render_sidebar()

page_header("Expense Management", "Track business overheads, bills, and operational costs", "💸")

tab_record, tab_history, tab_summary = st.tabs([
    "➕ **Record Expense**",
    "📜 **History**",
    "📊 **Summary**"
])

# ── RECORD EXPENSE ──
with tab_record:
    st.markdown('<div class="section-header">Record New Business Expense</div>', unsafe_allow_html=True)
    
    with st.form("expense_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            category = st.selectbox("Category", [
                "Rent", "Electricity", "Water", "Salaries", 
                "Marketing", "Internet", "Maintenance", "Supplies", "Others"
            ])
            amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
        with c2:
            e_date = st.date_input("Expense Date", value=datetime.now())
            description = st.text_input("Description (Optional)")
            
        submitted = st.form_submit_button("Record Expense")
        if submitted:
            if amount <= 0:
                st.error("Amount must be greater than zero.")
            else:
                with st.spinner("Saving expense..."):
                    res = expense_logic.record_expense(category, amount, description, e_date.isoformat())
                    if res['success']:
                        st.success(res['message'])
                    else:
                        st.error(res['message'])

# ── HISTORY ──
with tab_history:
    st.markdown('<div class="section-header">Expense Audit Log</div>', unsafe_allow_html=True)
    expenses = expense_logic.get_all_expenses()
    
    if not expenses:
        st.info("No expense records found.", icon="📜")
    else:
        df = pd.DataFrame(expenses)
        df = df[['expense_date', 'category', 'amount', 'description']]
        df.columns = ['Date', 'Category', 'Amount (₹)', 'Description']
        st.dataframe(df, use_container_width=True)

# ── SUMMARY ──
with tab_summary:
    st.markdown('<div class="section-header">Overhead Analysis</div>', unsafe_allow_html=True)
    
    period = st.selectbox("View Period", [30, 90, 365], format_func=lambda x: f"Last {x} Days")
    
    summary = expense_logic.get_expense_summary(period)
    
    if summary.get("error"):
        st.error(summary['error'])
    else:
        st.markdown(kpi_card("Total Overhead", f"₹{summary['total']:,.2f}", "💸", "red"), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        breakdown = summary['breakdown']
        if not breakdown:
            st.info("No data for the selected period.")
        else:
            fig = go.Figure(data=[go.Pie(
                labels=list(breakdown.keys()),
                values=list(breakdown.values()),
                hole=0.5,
                marker=dict(line=dict(color='rgba(0,0,0,0.3)', width=2)),
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>₹%{value:,.2f}<extra></extra>'
            )])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter', color='rgba(226,232,240,0.6)'),
                height=400,
                legend=dict(font=dict(size=11))
            )
            st.plotly_chart(fig, use_container_width=True)
