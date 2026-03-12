import streamlit as st
import pandas as pd
from nexus_commerce.inventory import logic as inv_logic
from nexus_commerce.common._utils import inject_custom_css, render_sidebar, page_header, kpi_card, status_pill, render_notification

# ── Page Config ──
st.set_page_config(page_title="Inventory | Nexus Commerce", layout="wide", page_icon="📦")
if not st.session_state.get("authenticated"):
    st.error("🔒 You must be logged in."); st.stop()

inject_custom_css()
render_sidebar()

render_notification()

page_header("Inventory Management", "Full CRUD operations — Add, View, Update, Delete & Adjust Stock", "📦")

# ── Load Products ──
products = inv_logic.get_all_products()
product_list = products if isinstance(products, list) else []

# ── KPI Row ──
total = len(product_list)
in_stock = sum(1 for p in product_list if p.get('quantity_on_hand', 0) >= 10)
low_stock = sum(1 for p in product_list if 0 < p.get('quantity_on_hand', 0) < 10)
out_of_stock = sum(1 for p in product_list if p.get('quantity_on_hand', 0) == 0)

c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(kpi_card("Total Products", str(total), "📦", "blue"), unsafe_allow_html=True)
with c2: st.markdown(kpi_card("In Stock", str(in_stock), "✅", "green"), unsafe_allow_html=True)
with c3: st.markdown(kpi_card("Low Stock", str(low_stock), "⚠️", "amber"), unsafe_allow_html=True)
with c4: st.markdown(kpi_card("Out of Stock", str(out_of_stock), "🚨", "red"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs for CRUD Operations ──
tab_view, tab_add, tab_update, tab_adjust, tab_delete = st.tabs([
    "📋 **View Products**",
    "➕ **Add Product**",
    "✏️ **Update Product**",
    "📊 **Adjust Stock**",
    "🗑️ **Delete Product**"
])

# ── VIEW PRODUCTS ──
with tab_view:
    if not product_list:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📦</div>
            <div class="empty-title">No Products Yet</div>
            <div class="empty-desc">Add your first product using the "Add Product" tab.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        search = st.text_input("🔍 Search products by name or SKU…", key="prod_search", placeholder="e.g. Laptop, SKU001")
        filtered = [p for p in product_list if search.lower() in p['name'].lower() or search.lower() in p['sku'].lower()] if search else product_list

        st.caption(f"Showing {len(filtered)} of {total} products")

        # Inventory summary
        summary = inv_logic.get_inventory_summary()
        if not summary.get("error"):
            sc1, sc2, sc3 = st.columns(3)
            with sc1: st.markdown(kpi_card("Stock Value (Cost)", f"₹{summary['total_cost_value']:,.0f}", "🏷️", "blue"), unsafe_allow_html=True)
            with sc2: st.markdown(kpi_card("Stock Value (Retail)", f"₹{summary['total_sell_value']:,.0f}", "💳", "green"), unsafe_allow_html=True)
            with sc3: st.markdown(kpi_card("Potential Profit", f"₹{summary['potential_profit']:,.0f}", "🎯", "amber"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Build display DataFrame
        df = pd.DataFrame(filtered)
        if not df.empty:
            # Defensive check: Ensure all columns exist
            required_cols = ['sku', 'name', 'cost_price', 'selling_price', 'quantity_on_hand']
            for col in required_cols:
                if col not in df.columns:
                    df[col] = 0 if 'price' in col or 'quantity' in col else "N/A"
            
            display_df = df[required_cols].copy()
            display_df.columns = ['SKU', 'Product Name', 'Cost Price (₹)', 'Selling Price (₹)', 'Stock']
            display_df['Margin (₹)'] = display_df['Selling Price (₹)'] - display_df['Cost Price (₹)']
            st.dataframe(display_df, use_container_width=True, hide_index=True)

            # CSV Export
            csv = display_df.to_csv(index=False)
            st.download_button("📥 Export to CSV", csv, "nexus_inventory.csv", "text/csv", use_container_width=True)

# ── ADD PRODUCT ──
with tab_add:
    st.markdown('<div class="section-header">Add New Product</div>', unsafe_allow_html=True)
    with st.form("add_product_form"):
        st.text_input("Product Name", key="ap_name", placeholder="e.g. Premium Wireless Headphones")
        st.text_input("SKU (Unique Code)", key="ap_sku", placeholder="e.g. SKU001")
        ac1, ac2 = st.columns(2)
        with ac1: st.number_input("Cost Price (₹)", key="ap_cost", min_value=0.0, format="%.2f", step=1.0)
        with ac2: st.number_input("Selling Price (₹)", key="ap_sell", min_value=0.0, format="%.2f", step=1.0)
        st.number_input("Initial Stock Quantity", key="ap_qty", min_value=0, step=1)
        submitted = st.form_submit_button("➕ Add Product", use_container_width=True, type="primary")

        if submitted:
            name = st.session_state.ap_name
            sku = st.session_state.ap_sku
            cost = st.session_state.ap_cost
            sell = st.session_state.ap_sell
            qty = st.session_state.ap_qty

            if not name or not sku:
                st.error("Product name and SKU are required.", icon="🚨")
            elif sell < cost:
                st.warning("Selling price is less than cost price. This product will operate at a loss.", icon="⚠️")
            else:
                result = inv_logic.add_product(name, sku, cost, sell, qty)
                if result.startswith("Success"):
                    st.session_state.toast_msg = result
                    st.rerun()
                else:
                    st.error(result, icon="🚨")

# ── UPDATE PRODUCT ──
with tab_update:
    st.markdown('<div class="section-header">Update Product Details</div>', unsafe_allow_html=True)
    with st.form("update_product_form"):
        sku_list = [p['sku'] for p in product_list]
        if sku_list:
            selected_sku = st.selectbox("Select Product (SKU)", sku_list, key="up_sku")
            selected = next((p for p in product_list if p['sku'] == selected_sku), None)

            if selected:
                st.info(f"Currently editing: **{selected['name']}**", icon="ℹ️")
                new_name = st.text_input("New Name", value=selected['name'], key="up_name")
                uc1, uc2 = st.columns(2)
                with uc1: new_cost = st.number_input("New Cost Price (₹)", value=float(selected['cost_price']), min_value=0.0, format="%.2f", key="up_cost")
                with uc2: new_sell = st.number_input("New Selling Price (₹)", value=float(selected['selling_price']), min_value=0.0, format="%.2f", key="up_sell")
                submitted = st.form_submit_button("✏️ Update Product", use_container_width=True, type="primary")

                if submitted:
                    updates = {"name": new_name.strip(), "cost_price": new_cost, "selling_price": new_sell}
                    result = inv_logic.update_product_by_sku(selected_sku, updates)
                    if result.startswith("Success"):
                        st.session_state.toast_msg = result
                        st.rerun()
                    else:
                        st.error(result, icon="🚨")
        else:
            st.info("No products available to update.", icon="📦")
            st.form_submit_button("Update", disabled=True)

# ── ADJUST STOCK ──
with tab_adjust:
    st.markdown('<div class="section-header">Stock Adjustment</div>', unsafe_allow_html=True)
    with st.form("adjust_stock_form"):
        sku_list = [p['sku'] for p in product_list]
        if sku_list:
            adj_sku = st.selectbox("Select Product (SKU)", sku_list, key="adj_sku")
            adj_product = next((p for p in product_list if p['sku'] == adj_sku), None)
            if adj_product:
                st.info(f"**{adj_product['name']}** — Current stock: **{adj_product['quantity_on_hand']}** units", icon="📊")
            change = st.number_input("Quantity Change (+ to add, - to remove)", step=1, key="adj_qty")
            reason = st.text_input("Reason for Adjustment", key="adj_reason", placeholder="e.g. New shipment arrived, Damaged goods")
            submitted = st.form_submit_button("📊 Apply Adjustment", use_container_width=True, type="primary")

            if submitted:
                if change == 0:
                    st.warning("Change quantity cannot be zero.", icon="⚠️")
                elif not reason:
                    st.error("Please provide a reason for the adjustment.", icon="🚨")
                else:
                    result = inv_logic.adjust_stock_quantity(adj_sku, change, reason)
                    if result.startswith("Success"):
                        st.session_state.toast_msg = result
                        st.rerun()
                    else:
                        st.error(result, icon="🚨")
        else:
            st.info("No products available for adjustment.", icon="📦")
            st.form_submit_button("Adjust", disabled=True)

# ── DELETE PRODUCT ──
with tab_delete:
    st.markdown('<div class="section-header">Delete Product</div>', unsafe_allow_html=True)
    st.warning("⚠️ **Caution**: Deleting a product is permanent and cannot be undone. Products with existing sales records cannot be deleted.", icon="⚠️")

    with st.form("delete_product_form"):
        sku_list = [p['sku'] for p in product_list]
        if sku_list:
            del_sku = st.selectbox("Select Product to Delete", sku_list, key="del_sku")
            del_product = next((p for p in product_list if p['sku'] == del_sku), None)
            if del_product:
                st.error(f"You are about to delete: **{del_product['name']}** (SKU: {del_sku}) — Stock: {del_product['quantity_on_hand']} units", icon="🗑️")
            confirm = st.text_input("Type the SKU to confirm deletion", key="del_confirm", placeholder=f"Type '{del_sku}' to confirm")
            submitted = st.form_submit_button("🗑️ Delete Product Permanently", use_container_width=True, type="primary")

            if submitted:
                if confirm.strip().upper() != del_sku:
                    st.error(f"SKU confirmation does not match. Expected: {del_sku}", icon="🚨")
                else:
                    result = inv_logic.delete_product_by_sku(del_sku)
                    if result.startswith("Success"):
                        st.session_state.toast_msg = result
                        st.rerun()
                    else:
                        st.error(result, icon="🚨")
        else:
            st.info("No products available to delete.", icon="📦")
            st.form_submit_button("Delete", disabled=True)
