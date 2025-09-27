import streamlit as st
import pandas as pd
from datetime import datetime
from nexus_commerce.inventory import logic as inventory_logic
from nexus_commerce.customers import logic as customer_logic
from nexus_commerce.reports import logic as report_logic

# --- Page Configuration and Authentication ---
st.set_page_config(page_title="Dashboard", layout="wide", page_icon="📊")

# This is a critical security measure. It checks if the user is logged in
# by looking at the session state. If not, it stops the page from loading.
if not st.session_state.get("authenticated"):
    st.error("🔒 You must be logged in to view this page. Please go to the main page to log in.")
    st.stop()

# --- Sidebar ---
# This creates a consistent sidebar for a professional look and feel.
st.sidebar.title(f"Welcome, {st.session_state.user_email}")
st.sidebar.divider()
if st.sidebar.button("Logout", key="dashboard_logout", use_container_width=True):
    # When logout is clicked, it clears the session state and redirects to the login page.
    st.session_state.authenticated = False
    st.session_state.user_email = ""
    st.switch_page("app.py")

# --- Main Page Content ---
st.title("📊 Business Dashboard")
st.markdown(f"An overview of your business operations as of {datetime.now().strftime('%d %b %Y, %I:%M %p')}")

# --- Key Performance Indicator (KPI) Metrics ---
st.divider()
col1, col2, col3 = st.columns(3)

# Using a spinner provides a better user experience while data is being fetched.
with st.spinner("Loading key metrics..."):
    # Fetch data from all relevant logic modules.
    products = inventory_logic.get_all_products()
    customers = customer_logic.get_all_customers()
    daily_report = report_logic.get_profit_report('daily')

    # Safely calculate metrics, handling potential errors from the logic layer.
    total_products = len(products) if isinstance(products, list) else 0
    total_customers = len(customers) if isinstance(customers, list) else 0
    daily_revenue = daily_report.get('total_revenue', 0)

    # Display the KPIs in styled metric boxes.
    col1.metric("Total Products", f"{total_products}", help="The total number of unique products in your inventory.")
    col2.metric("Total Customers", f"{total_customers}", help="The total number of customers registered in the system.")
    col3.metric("Revenue (Last 24h)", f"Rs. {daily_revenue:.2f}", help="Total sales revenue generated in the last 24 hours.")

# --- Interactive Sales Trend Chart ---
st.divider()
st.subheader("Sales Trend Analysis")

# This interactive selectbox allows the user to control the chart's time window.
time_window = st.selectbox(
    "Select Time Window",
    (7, 30, 90),
    format_func=lambda x: f"Last {x} Days",
    index=1  # Default to 30 days
)

with st.spinner(f"Loading sales data for the last {time_window} days..."):
    sales_response = report_logic.get_sales_over_time(time_window)
    
    if "error" in sales_response:
        st.error(sales_response['error'], icon="🚨")
    else:
        sales_data = sales_response.get("data", [])
        if not sales_data:
            st.info(f"No sales data available for the last {time_window} days to display a chart.")
        else:
            # Use Pandas to process the data for charting.
            df = pd.DataFrame(sales_data)
            df['sale_date'] = pd.to_datetime(df['sale_date']).dt.date
            # Group by date and sum the amounts to get daily sales totals.
            daily_sales = df.groupby('sale_date')['total_amount'].sum()
            
            # Calculate additional KPIs for the selected period.
            total_period_revenue = daily_sales.sum()
            best_day_revenue = daily_sales.max()
            best_day_date = daily_sales.idxmax().strftime('%d %b %Y') if not daily_sales.empty else "N/A"
            
            kpi_col1, kpi_col2 = st.columns(2)
            kpi_col1.metric(f"Total Revenue (Last {time_window} Days)", f"Rs. {total_period_revenue:.2f}")
            kpi_col2.metric(f"Best Sales Day", f"Rs. {best_day_revenue:.2f}", help=f"On {best_day_date}")
            
            # Use an Area Chart for a more professional and attractive visual.
            st.area_chart(daily_sales)

# --- Quick Actions Section ---
st.divider()
st.subheader("Quick Actions")
qcol1, qcol2, qcol3 = st.columns(3)

# These buttons allow for quick navigation to the most frequently used pages.
if qcol1.button("➕ Add New Product", use_container_width=True):
    st.switch_page("pages/2_Inventory_Management.py")
if qcol2.button("🛒 Record a New Sale", use_container_width=True):
    st.switch_page("pages/3_Record_Sale.py")
if qcol3.button("👥 Add New Customer", use_container_width=True):
    st.switch_page("pages/4_Customer_Management.py")

