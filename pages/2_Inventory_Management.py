import streamlit as st
import pandas as pd
from nexus_commerce.inventory import logic

# --- Page Configuration and Authentication ---
# This sets the title that appears in the browser tab and configures the layout.
st.set_page_config(page_title="Inventory Management", layout="wide", page_icon="📦")

# This is a critical security measure. It checks if the user is logged in
# by looking at the session state. If not, it stops the page from loading.
if not st.session_state.get("authenticated"):
    st.error("🔒 You must be logged in to view this page. Please go to the main page to log in.")
    st.stop()

# --- Sidebar ---
# This creates a consistent sidebar for a professional look and feel.
st.sidebar.title(f"Welcome, {st.session_state.user_email}")
st.sidebar.divider()
if st.sidebar.button("Logout", key="inventory_logout", use_container_width=True):
    # When logout is clicked, it clears the session state and redirects to the login page.
    st.session_state.authenticated = False
    st.session_state.user_email = ""
    st.switch_page("app.py")

st.title("📦 Inventory Management")

# --- UI organized into tabs for different actions ---
tab1, tab2, tab3, tab4 = st.tabs(["**View All Products**", "**Add New Product**", "**Update Product**", "**Adjust Stock**"])

# --- TAB 1: VIEW ALL PRODUCTS ---
with tab1:
    st.header("Current Inventory")
    
    with st.spinner("Fetching product data..."):
        products = logic.get_all_products()
    
    if isinstance(products, list) and products:
        df = pd.DataFrame(products)
        # Prepare the DataFrame for a clean display
        df_display = df[['sku', 'name', 'quantity_on_hand', 'cost_price', 'selling_price']]
        df_display.rename(columns={
            'sku': 'SKU', 'name': 'Name', 'quantity_on_hand': 'Quantity',
            'cost_price': 'Cost (Rs)', 'selling_price': 'Price (Rs)'
        }, inplace=True)

        # --- Interactive Filter ---
        st.subheader("Filter Products")
        search_query = st.text_input("Search by Name or SKU", placeholder="Type to filter the list below...")
        if search_query:
            # Filter the DataFrame based on user input
            df_display = df_display[df_display['Name'].str.contains(search_query, case=False) | 
                                    df_display['SKU'].str.contains(search_query, case=False)]
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    elif not products:
        st.info("No products found in the inventory. Add one in the next tab!", icon="➕")
    else:
        # If the logic function returns an error string, display it.
        st.error(products, icon="🚨")

# --- TAB 2: ADD NEW PRODUCT ---
with tab2:
    st.header("Add a New Product")
    with st.form("add_product_form", clear_on_submit=True, border=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Product Name*")
            sku = st.text_input("Product SKU (Unique Code)*")
        with col2:
            cost_price = st.number_input("Cost Price (Rs)*", min_value=0.0, format="%.2f")
            selling_price = st.number_input("Selling Price (Rs)*", min_value=0.0, format="%.2f")
        quantity = st.number_input("Initial Quantity", min_value=0, step=1, help="The starting stock for this product.")
        
        submitted = st.form_submit_button("Add Product", use_container_width=True, type="primary")
        if submitted:
            if not all([name, sku]):
                st.error("Name and SKU are required fields.", icon="🚨")
            else:
                # Includes the safeguard to warn against unprofitable pricing.
                if selling_price <= cost_price:
                    st.warning(f"Warning: The selling price (Rs. {selling_price:.2f}) is not higher than the cost price (Rs. {cost_price:.2f}).")
                with st.spinner("Adding product..."):
                    result = logic.add_product(name, sku, cost_price, selling_price, quantity)
                if "Success" in result: 
                    st.success(result, icon="✅")
                else: 
                    st.error(result, icon="🚨")

# --- TAB 3: UPDATE PRODUCT DETAILS ---
with tab3:
    st.header("Update Product Details")
    sku_to_update = st.text_input("Enter SKU to find and update", key="update_sku", placeholder="e.g., M32")
    if sku_to_update:
        product = logic.find_product_by_sku(sku_to_update)
        if isinstance(product, dict):
            # The update form is only shown after a valid product is found.
            with st.form("update_product_form", border=True):
                st.info(f"You are updating **{product['name']}**.", icon="✏️")
                new_name = st.text_input("New Name", value=product['name'])
                new_selling_price = st.number_input("New Selling Price (Rs)", value=float(product['selling_price']))
                new_cost_price = st.number_input("New Cost Price (Rs)", value=float(product['cost_price']))
                
                update_submitted = st.form_submit_button("Update Product Details", use_container_width=True, type="primary")
                if update_submitted:
                    updates = {}
                    if new_name != product['name']: updates['name'] = new_name
                    if new_selling_price != product['selling_price']: updates['selling_price'] = new_selling_price
                    if new_cost_price != product['cost_price']: updates['cost_price'] = new_cost_price
                    if not updates: 
                        st.warning("No changes were made.", icon="⚠️")
                    else:
                        with st.spinner("Updating..."):
                            result = logic.update_product_by_sku(sku_to_update, updates)
                        if "Success" in result: 
                            st.success(result, icon="✅")
                        else: 
                            st.error(result, icon="🚨")
        elif product is None: 
            st.warning(f"No product found with SKU '{sku_to_update.upper()}'.", icon="⚠️")
        else: 
            st.error(product, icon="🚨")

# --- TAB 4: ADJUST STOCK QUANTITY ---
with tab4:
    st.header("Adjust Stock Quantity")
    st.info("Use this for manual corrections like damaged items or physical stock counts. This creates an audit trail.", icon="ℹ️")
    with st.form("adjust_stock_form", clear_on_submit=True, border=True):
        sku_to_adjust = st.text_input("Product SKU*", placeholder="e.g., M32")
        change_quantity = st.number_input("Change in Quantity*", step=1, value=0, help="e.g., -1 for removal, 5 for addition")
        reason = st.text_input("Reason for adjustment (Required)*", placeholder="e.g., Damaged item")
        
        adjust_submitted = st.form_submit_button("Adjust Stock", use_container_width=True, type="primary")
        if adjust_submitted:
            if not all([sku_to_adjust, reason, change_quantity != 0]):
                st.error("SKU, a non-zero quantity, and a Reason are required.", icon="🚨")
            else:
                with st.spinner("Adjusting stock and creating audit record..."):
                    result = logic.adjust_stock_quantity(sku_to_adjust, change_quantity, reason)
                if "Success" in result: 
                    st.success(result, icon="✅")
                else: 
                    st.error(result, icon="🚨")

