import streamlit as st
import pandas as pd
from nexus_commerce.reports import logic

# --- Page Configuration and Authentication ---
# This sets the title that appears in the browser tab and configures the layout.
st.set_page_config(page_title="Business Reports", layout="wide", page_icon="📊")

# This is a critical security measure. It checks if the user is logged in
# by looking at the session state. If not, it stops the page from loading.
if not st.session_state.get("authenticated"):
    st.error("🔒 You must be logged in to view this page. Please go to the main page to log in.")
    st.stop()

# --- Sidebar ---
# This creates a consistent sidebar for a professional look and feel.
st.sidebar.title(f"Welcome, {st.session_state.user_email}")
st.sidebar.divider()
if st.sidebar.button("Logout", key="reports_logout", use_container_width=True):
    # When logout is clicked, it clears the session state and redirects to the login page.
    st.session_state.authenticated = False
    st.session_state.user_email = ""
    st.switch_page("app.py")

st.title("📊 Business Intelligence Reports")

# --- UI organized into tabs for each report ---
tab1, tab2, tab3, tab4 = st.tabs(["**Profit & Revenue**", "**Product Health**", "**Payment Summary**", "**Sale Simulator**"])

# --- TAB 1: PROFIT & REVENUE ---
with tab1:
    st.header("Profit & Revenue Report")
    period = st.selectbox("Select Period", ['daily', 'weekly', 'monthly'], key='profit_period', help="View financial performance over a selected time window.")
    
    if st.button("Generate Profit Report", use_container_width=True, type="primary"):
        with st.spinner("Calculating..."):
            response = logic.get_profit_report(period)
        
        if "error" in response:
            st.error(response["error"], icon="🚨")
        else:
            start_date = response['start_date'].strftime('%d %b %Y')
            end_date = response['end_date'].strftime('%d %b %Y')
            st.subheader(f"Report for period: {start_date} to {end_date}")
            
            # st.metric is a great way to display key performance indicators (KPIs).
            col1, col2 = st.columns(2)
            col1.metric("Total Revenue", f"Rs. {response['total_revenue']:.2f}")
            col2.metric("Total Profit", f"Rs. {response['total_profit']:.2f}")

# --- TAB 2: PRODUCT HEALTH ---
with tab2:
    st.header("Product Health Status")
    st.info("Categorizes products based on sales velocity to identify top performers and stagnant stock.", icon="ℹ️")
    
    if st.button("Generate Health Report", use_container_width=True, type="primary"):
        with st.spinner("Analyzing product health..."):
            response = logic.get_product_health_report()
            
        if "error" in response:
            st.error(response["error"], icon="🚨")
        else:
            products = response.get("data", [])
            if not products:
                st.warning("No products found to report on.", icon="⚠️")
            else:
                df = pd.DataFrame(products)
                st.dataframe(df, use_container_width=True, hide_index=True,
                             column_config={"sku": "SKU", "name": "Name", "quantity": "Qty", "status": "Status"})

# --- TAB 3: PAYMENT SUMMARY ---
with tab3:
    st.header("Payment Methods Summary")
    period_payment = st.selectbox("Select Period", ['daily', 'weekly', 'monthly'], key='payment_period', help="See how customers are paying.")
    
    if st.button("Generate Payment Summary", use_container_width=True, type="primary"):
        with st.spinner("Summarizing payments..."):
            response = logic.get_payment_summary(period_payment)
            
        if "error" in response:
            st.error(response["error"], icon="🚨")
        else:
            start_date = response['start_date'].strftime('%d %b %Y')
            end_date = response['end_date'].strftime('%d %b %Y')
            summary = response.get("summary", {})
            
            st.subheader(f"Report for period: {start_date} to {end_date}")
            if not summary:
                st.warning("No payments recorded in this period.", icon="⚠️")
            else:
                summary_df = pd.DataFrame(list(summary.items()), columns=['Payment Method', 'Total Amount (Rs)'])
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
                # Adding a bar chart provides a nice visual summary.
                st.bar_chart(summary_df.set_index('Payment Method'))

# --- TAB 4: SALE SIMULATOR ---
with tab4:
    st.header("Sale Simulator")
    st.info("Test the financial impact of a discount before you run a promotion.", icon="💡")
    
    with st.form("simulator_form", border=True):
        discount = st.number_input("Discount Percentage (%)", min_value=0.1, max_value=99.9, value=10.0, step=0.1, help="Enter a value like 10 for 10%")
        sku_input = st.text_input("Enter Product SKUs (comma-separated)", placeholder="e.g., M32, BOAT-H")
        
        sim_submitted = st.form_submit_button("Simulate Sale", use_container_width=True, type="primary")
        if sim_submitted and sku_input:
            skus = [sku.strip().upper() for sku in sku_input.split(',')]
            
            with st.spinner("Running simulation..."):
                response = logic.simulate_sale(discount, skus)
                
            results = response.get("data", [])
            if not results:
                st.warning("Could not simulate sale. Check if SKUs are correct.", icon="⚠️")
            else:
                st.subheader(f"Simulation Results for a {discount}% Discount")
                sim_df = pd.DataFrame(results)
                
                # Handle not-found errors gracefully
                if 'error' in sim_df.columns:
                    st.error("Some products were not found:")
                    st.dataframe(sim_df[sim_df['error'].notna()][['sku', 'error']], use_container_width=True, hide_index=True)
                    sim_df = sim_df.dropna(subset=['name']) # Filter out errors for the main table
                
                if not sim_df.empty:
                    st.dataframe(sim_df, use_container_width=True, hide_index=True,
                                 column_config={"sku": "SKU", "name": "Name",
                                                "original_price": st.column_config.NumberColumn("Original Price", format="Rs. %.2f"),
                                                "discounted_price": st.column_config.NumberColumn("Discounted Price", format="Rs. %.2f"),
                                                "original_profit": st.column_config.NumberColumn("Original Profit", format="Rs. %.2f"),
                                                "new_profit": st.column_config.NumberColumn("New Profit", format="Rs. %.2f")})
                    
                    # Highlight critical insights about potential losses
                    losing_products = sim_df[sim_df['new_profit'] < 0]
                    if not losing_products.empty:
                        st.warning("⚠️ **Critical Insights:**")
                        for _, row in losing_products.iterrows():
                            st.write(f"- A **{discount}% discount** on **'{row['name']}'** will result in a **LOSS of Rs. {-row['new_profit']:.2f}** per unit.")

