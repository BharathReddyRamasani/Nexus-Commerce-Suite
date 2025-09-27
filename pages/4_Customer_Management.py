import streamlit as st
import pandas as pd
from nexus_commerce.customers import logic

# --- Page Configuration and Authentication ---
# This sets the title that appears in the browser tab and configures the layout.
st.set_page_config(page_title="Customer Management", layout="wide", page_icon="👥")

# This is a critical security measure. It checks if the user is logged in
# by looking at the session state. If not, it stops the page from loading.
if not st.session_state.get("authenticated"):
    st.error("🔒 You must be logged in to view this page. Please go to the main page to log in.")
    st.stop()

# --- Sidebar ---
# This creates a consistent sidebar for a professional look and feel.
st.sidebar.title(f"Welcome, {st.session_state.user_email}")
st.sidebar.divider()
if st.sidebar.button("Logout", key="customer_logout", use_container_width=True):
    # When logout is clicked, it clears the session state and redirects to the login page.
    st.session_state.authenticated = False
    st.session_state.user_email = ""
    st.switch_page("app.py")

st.title("👥 Customer Management (CRM)")

# --- UI organized into tabs for different CRM actions ---
tab1, tab2, tab3 = st.tabs(["**View All Customers**", "**Add New Customer**", "**View Customer History**"])

# --- TAB 1: VIEW ALL CUSTOMERS ---
with tab1:
    st.header("Customer List")
    customers = logic.get_all_customers()
    if isinstance(customers, list):
        if not customers:
            st.info("No customers found. Add one in the next tab!", icon="➕")
        else:
            df = pd.DataFrame(customers)
            # Select and reorder columns for a clean presentation.
            df_display = df[['name', 'phone', 'email', 'created_at']]
            df_display.rename(columns={'name': 'Name', 'phone': 'Phone', 'email': 'Email', 'created_at': 'Date Added'}, inplace=True)
            st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        # Handles the case where the logic function returns an error string.
        st.error(customers, icon="🚨")

# --- TAB 2: ADD NEW CUSTOMER ---
with tab2:
    st.header("Add a New Customer")
    # Using a form prevents the page from rerunning on every input change.
    with st.form("add_customer_form", clear_on_submit=True, border=True):
        name = st.text_input("Customer Name*")
        phone = st.text_input("Customer Phone Number*")
        email = st.text_input("Customer Email (Optional)")

        submitted = st.form_submit_button("Add Customer", use_container_width=True, type="primary")
        if submitted:
            if not all([name, phone]):
                st.error("Name and Phone are required.", icon="🚨")
            else:
                with st.spinner("Adding customer..."):
                    result = logic.add_customer(name, phone, email)
                if "Success" in result:
                    st.success(result, icon="✅")
                else:
                    st.error(result, icon="🚨")

# --- TAB 3: VIEW CUSTOMER HISTORY ---
with tab3:
    st.header("View Customer Purchase History")
    phone_to_find = st.text_input("Enter customer phone number to find history", key="find_phone")
    
    if st.button("Find History", use_container_width=True) and phone_to_find:
        with st.spinner(f"Searching for history of {phone_to_find}..."):
            customer = logic.find_customer_by_phone(phone_to_find)
        
        if isinstance(customer, str): # Error message returned from logic
            st.error(customer, icon="🚨")
        elif customer is None:
            st.warning(f"No customer found with phone '{phone_to_find}'.", icon="⚠️")
        else:
            st.subheader(f"Purchase History for: {customer['name']} ({customer['phone']})")
            
            if not customer.get('sales'):
                st.info("This customer has no purchase history.", icon="ℹ️")
            else:
                # Sort sales by date, most recent first, for a better user experience.
                for sale in sorted(customer['sales'], key=lambda s: s['sale_date'], reverse=True):
                    # st.expander creates a clean, collapsible view for each sale.
                    with st.expander(f"**Sale on {sale['sale_date']}** | Total: Rs. {sale['total_amount']:.2f}"):
                        if not sale.get('items'):
                            st.write("No item details found for this sale.")
                        else:
                            # Prepare data for a clean table display inside the expander.
                            items_data = []
                            for item in sale['items']:
                                # Safely access nested product info to prevent errors.
                                product_info = item.get('products', {})
                                items_data.append({
                                    "Product Name": product_info.get('name', 'N/A'),
                                    "SKU": product_info.get('sku', 'N/A'),
                                    "Quantity": item['quantity'],
                                    "Price per Unit": item['price_per_unit']
                                })
                            items_df = pd.DataFrame(items_data)
                            st.dataframe(items_df, use_container_width=True, hide_index=True)

