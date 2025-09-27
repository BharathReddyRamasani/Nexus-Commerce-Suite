import streamlit as st
import pandas as pd
import time
from nexus_commerce.sales import logic as sales_logic
from nexus_commerce.inventory import logic as inventory_logic

# --- Page Configuration and Authentication ---
st.set_page_config(page_title="Sales Terminal", layout="wide", page_icon="🛒")

# This is a critical security measure to protect the page.
if not st.session_state.get("authenticated"):
    st.error("🔒 You must be logged in to view this page. Please go to the main page to log in.")
    st.stop()

# --- Sidebar ---
st.sidebar.title(f"Welcome, {st.session_state.user_email}")
st.sidebar.divider()
if st.sidebar.button("Logout", key="sales_logout", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.user_email = ""
    st.switch_page("app.py")

st.title("🛒 Sales Terminal")

# --- Session State Initialization ---
# This is crucial for Streamlit apps. It creates a "memory" for the cart
# and payments that persists between user interactions (reruns).
if 'cart_items' not in st.session_state:
    st.session_state.cart_items = []
if 'payments' not in st.session_state:
    st.session_state.payments = []

# --- Layout with Columns for a clean Point-of-Sale feel ---
col1, col2 = st.columns([1.5, 2])

# --- COLUMN 1: Adding Items and Payments ---
with col1:
    # Container for adding items
    with st.container(border=True):
        st.subheader("1. Add Items to Sale")
        with st.form("add_item_form"):
            sku_to_add = st.text_input("Product SKU")
            quantity_to_add = st.number_input("Quantity", min_value=1, step=1)
            add_item_submitted = st.form_submit_button("Add Item", use_container_width=True)

            if add_item_submitted and sku_to_add:
                product = inventory_logic.find_product_by_sku(sku_to_add)
                if isinstance(product, dict):
                    # Add found product to our session state list
                    st.session_state.cart_items.append({
                        "sku": sku_to_add.upper(), "name": product['name'],
                        "quantity": quantity_to_add, "price": product['selling_price']
                    })
                    # st.rerun() immediately refreshes the page to show the updated cart
                    st.rerun()
                else:
                    st.error(f"Product with SKU '{sku_to_add}' not found.", icon="🚨")
    
    # Container for adding payments
    with st.container(border=True):
        st.subheader("2. Add Payments")
        with st.form("add_payment_form"):
            payment_method = st.selectbox("Payment Method", ["Cash", "UPI", "Card"])
            payment_amount = st.number_input("Amount (Rs)", min_value=0.01, format="%.2f")
            add_payment_submitted = st.form_submit_button("Add Payment", use_container_width=True)

            if add_payment_submitted and payment_amount > 0:
                st.session_state.payments.append({"method": payment_method, "amount": payment_amount})
                st.rerun()

# --- COLUMN 2: Sale Summary and Finalization ---
with col2:
    with st.container(border=True):
        st.subheader("Current Sale Summary")
        if not st.session_state.cart_items:
            st.info("Cart is empty. Add items to begin a sale.", icon="🛒")
        else:
            # --- Display Cart Items ---
            cart_df = pd.DataFrame(st.session_state.cart_items)
            cart_df['Subtotal'] = cart_df['quantity'] * cart_df['price']
            st.write("**Items in Cart:**")
            st.dataframe(cart_df[['name', 'sku', 'quantity', 'price', 'Subtotal']], use_container_width=True, hide_index=True)
            sale_total = cart_df['Subtotal'].sum()
            
            # --- Display Payments ---
            payments_df = pd.DataFrame(st.session_state.payments)
            paid_total = payments_df['amount'].sum() if not payments_df.empty else 0
            
            # --- Display KPIs ---
            mcol1, mcol2, mcol3 = st.columns(3)
            mcol1.metric("Sale Total", f"Rs. {sale_total:.2f}")
            mcol2.metric("Total Paid", f"Rs. {paid_total:.2f}")
            
            # --- Calculate and Display Balance ---
            balance_due = sale_total - paid_total
            if balance_due > 0.01:
                mcol3.metric("Balance Due", f"Rs. {balance_due:.2f}", delta_color="inverse")
            elif balance_due < -0.01:
                mcol3.metric("Change Due", f"Rs. {-balance_due:.2f}", delta_color="normal")
            else:
                mcol3.metric("Balance", "Paid in Full", delta_color="off")
            
            st.divider()
            st.subheader("3. Finalize Sale")
            customer_phone = st.text_input("Customer Phone (Optional)", placeholder="Search by phone number to link sale")
            
            # --- Action Buttons ---
            fcol1, fcol2 = st.columns(2)
            if fcol1.button("✅ Complete Sale", use_container_width=True, type="primary"):
                items_for_logic = [{"sku": item['sku'], "quantity": item['quantity']} for item in st.session_state.cart_items]
                
                with st.spinner("Processing sale..."):
                    # Call the backend logic function to process the sale
                    result = sales_logic.record_sale(items_for_logic, st.session_state.payments, customer_phone.strip() or None)
                
                if result['success']:
                    st.success(result['message'], icon="🎉")
                    if result['alerts']:
                        for alert in result['alerts']:
                            st.warning(alert, icon="⚠️")
                    # Clear state for the next sale and celebrate!
                    st.session_state.cart_items = []
                    st.session_state.payments = []
                    st.balloons()
                    time.sleep(2) # Give time for balloons to show
                    st.rerun()
                else:
                    st.error(result['message'], icon="🚨")
            
            if fcol2.button("❌ Cancel Sale", use_container_width=True):
                st.session_state.cart_items = []
                st.session_state.payments = []
                st.info("Sale cancelled and cart cleared.", icon="🗑️")
                time.sleep(1)
                st.rerun()

