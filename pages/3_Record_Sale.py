import streamlit as st
from nexus_commerce.inventory import logic as inv_logic
from nexus_commerce.customers import logic as cust_logic
from nexus_commerce.sales import logic as sales_logic
from nexus_commerce.common._utils import inject_custom_css, render_sidebar, page_header, kpi_card, render_notification

# ── Page Config ──
st.set_page_config(page_title="Sales Terminal | Nexus Commerce", layout="wide", page_icon="🛒")
if not st.session_state.get("authenticated"):
    st.error("🔒 You must be logged in."); st.stop()

inject_custom_css()
render_sidebar()

render_notification()

page_header("Sales Terminal", "Point-of-Sale — Add items to cart and process transactions", "🛒")

# ── Session State for Cart ──
if "cart" not in st.session_state:
    st.session_state.cart = []

# ── Load Products ──
products = inv_logic.get_all_products()
product_list = products if isinstance(products, list) else []

# ── Two Column Layout ──
col_left, col_right = st.columns([3, 2])

# ── LEFT: Add to Cart ──
with col_left:
    st.markdown('<div class="section-header">🛍️ Add Items</div>', unsafe_allow_html=True)

    if not product_list:
        st.info("No products in inventory. Add products first.", icon="📦")
    else:
        available = [p for p in product_list if p['quantity_on_hand'] > 0]
        if not available:
            st.warning("All products are out of stock.", icon="⚠️")
        else:
            with st.form("add_to_cart_form"):
                product_options = {f"{p['name']} ({p['sku']}) — ₹{p['selling_price']:,.2f} — Stock: {p['quantity_on_hand']}": p['sku'] for p in available}
                selected_label = st.selectbox("Select Product", list(product_options.keys()))
                selected_sku = product_options[selected_label]
                selected_product = next(p for p in available if p['sku'] == selected_sku)

                qty = st.number_input("Quantity", min_value=1, max_value=selected_product['quantity_on_hand'], value=1, step=1)
                add_submitted = st.form_submit_button("🛒 Add to Cart", use_container_width=True, type="primary")

                if add_submitted:
                    # Check if already in cart
                    existing = next((item for item in st.session_state.cart if item['sku'] == selected_sku), None)
                    if existing:
                        max_qty = selected_product['quantity_on_hand']
                        if existing['quantity'] + qty > max_qty:
                            st.error(f"Cannot add more. Cart already has {existing['quantity']}, available: {max_qty}.", icon="🚨")
                        else:
                            existing['quantity'] += qty
                            st.session_state.toast_msg = f"Updated: {selected_product['name']} × {existing['quantity']}"
                            st.rerun()
                    else:
                        st.session_state.cart.append({
                            'sku': selected_sku,
                            'name': selected_product['name'],
                            'price': selected_product['selling_price'],
                            'quantity': qty
                        })
                        st.session_state.toast_msg = f"Added: {selected_product['name']} × {qty}"
                        st.rerun()

    # ── Customer (Optional) ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">👤 Customer (Optional)</div>', unsafe_allow_html=True)
    customers = cust_logic.get_all_customers()
    customer_list = customers if isinstance(customers, list) else []
    if customer_list:
        customer_options = {"No Customer (Walk-in)": ""} | {f"{c['name']} ({c['phone']})": c['phone'] for c in customer_list}
        selected_customer = st.selectbox("Link to Customer", list(customer_options.keys()))
        customer_phone = customer_options[selected_customer]
    else:
        customer_phone = ""
        st.caption("No customers registered. Sales will be recorded as walk-in.")

# ── RIGHT: Cart & Payment ──
with col_right:
    st.markdown('<div class="section-header">🧾 Cart Summary</div>', unsafe_allow_html=True)

    if not st.session_state.cart:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">🛒</div>
            <div class="empty-title">Cart is Empty</div>
            <div class="empty-desc">Add products from the left panel to start a sale.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        subtotal = 0
        total_tax = 0
        for i, item in enumerate(st.session_state.cart):
            # We need tax rate from product list
            prod = next(p for p in product_list if p['sku'] == item['sku'])
            tax_rate = prod.get('tax_rate', 0)
            
            line_subtotal = item['price'] * item['quantity']
            line_tax = line_subtotal * (tax_rate / 100.0)
            
            subtotal += line_subtotal
            total_tax += line_tax

            ic1, ic2, ic3 = st.columns([5, 2, 1])
            with ic1:
                st.markdown(f"**{item['name']}** `{item['sku']}`")
                tax_info = f" (+{tax_rate}% GST)" if tax_rate > 0 else ""
                st.caption(f"₹{item['price']:,.2f} × {item['quantity']} = ₹{line_subtotal:,.2f}{tax_info}")
            with ic3:
                if st.button("✕", key=f"rm_{i}", help="Remove from cart"):
                    st.session_state.cart.pop(i)
                    st.rerun()
            st.divider()

        # Total KPIs
        grand_total = subtotal + total_tax
        t1, t2, t3 = st.columns(3)
        with t1: st.markdown(kpi_card("Subtotal", f"₹{subtotal:,.2f}", "📦", "blue"), unsafe_allow_html=True)
        with t2: st.markdown(kpi_card("GST/Tax", f"₹{total_tax:,.2f}", "📜", "amber"), unsafe_allow_html=True)
        with t3: st.markdown(kpi_card("Total", f"₹{grand_total:,.2f}", "💰", "green"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Payment ──
        st.markdown('<div class="section-header">💳 Payment</div>', unsafe_allow_html=True)

        with st.form("payment_form"):
            method = st.selectbox("Payment Method", ["Cash", "Card", "UPI", "Bank Transfer"])
            amount = st.number_input(f"Amount (₹)", value=float(grand_total), min_value=0.0, format="%.2f")

            p1, p2 = st.columns(2)
            with p1: complete = st.form_submit_button("✅ Complete Sale", use_container_width=True, type="primary")
            with p2: cancel = st.form_submit_button("❌ Cancel", use_container_width=True)

            if complete:
                items = [{"sku": item['sku'], "quantity": item['quantity']} for item in st.session_state.cart]
                payments = [{"method": method, "amount": amount}]

                with st.spinner("Processing transaction…"):
                    result = sales_logic.record_sale(items, payments, customer_phone or None)

                if result['success']:
                    st.session_state.toast_msg = result['message']
                    for alert in result.get('alerts', []):
                        st.warning(alert, icon="⚠️")
                    st.session_state.cart = []
                    st.balloons()
                    st.rerun()
                else:
                    st.error(result['message'], icon="🚨")

            if cancel:
                st.session_state.cart = []
                st.info("Cart cleared.", icon="🗑️")
                st.rerun()
