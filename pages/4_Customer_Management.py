import streamlit as st
import pandas as pd
from nexus_commerce.customers import logic as cust_logic
from nexus_commerce.common._utils import inject_custom_css, render_sidebar, page_header, kpi_card, render_notification

# ── Page Config ──
st.set_page_config(page_title="Customers | Nexus Commerce", layout="wide", page_icon="👥")
if not st.session_state.get("authenticated"):
    st.error("🔒 You must be logged in."); st.stop()

inject_custom_css()
render_sidebar()

render_notification()

page_header("Customer Management", "Complete CRM — Add, View, Update, Delete & Analyze Customers", "👥")

# ── Load Data ──
customers = cust_logic.get_all_customers()
customer_list = customers if isinstance(customers, list) else []

# ── KPIs ──
total = len(customer_list)
with_email = sum(1 for c in customer_list if c.get('email'))
c1, c2, c3 = st.columns(3)
with c1: st.markdown(kpi_card("Total Customers", str(total), "👥", "purple"), unsafe_allow_html=True)
with c2: st.markdown(kpi_card("With Email", str(with_email), "📧", "blue"), unsafe_allow_html=True)
with c3: st.markdown(kpi_card("Without Email", str(total - with_email), "❓", "amber"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab_view, tab_add, tab_search, tab_update, tab_delete = st.tabs([
    "📋 **View All**",
    "➕ **Add Customer**",
    "🔍 **Search & History**",
    "✏️ **Update Customer**",
    "🗑️ **Delete Customer**"
])

# ── VIEW ALL ──
with tab_view:
    if not customer_list:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">👥</div>
            <div class="empty-title">No Customers Yet</div>
            <div class="empty-desc">Add your first customer using the "Add Customer" tab.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        search = st.text_input("🔍 Search by name or phone…", key="cust_search", placeholder="e.g. John, 9876543210")
        filtered = [c for c in customer_list if search.lower() in c.get('name', '').lower() or search in c.get('phone', '')] if search else customer_list

        st.caption(f"Showing {len(filtered)} of {total} customers")

        df = pd.DataFrame(filtered)
        if not df.empty:
            display_df = df[['name', 'phone', 'email']].copy()
            display_df.columns = ['Name', 'Phone', 'Email']
            display_df['Email'] = display_df['Email'].fillna('—')
            st.dataframe(display_df, use_container_width=True, hide_index=True)

            csv = display_df.to_csv(index=False)
            st.download_button("📥 Export Customers CSV", csv, "nexus_customers.csv", "text/csv", use_container_width=True)

# ── ADD CUSTOMER ──
with tab_add:
    st.markdown('<div class="section-header">Add New Customer</div>', unsafe_allow_html=True)
    with st.form("add_customer_form"):
        name = st.text_input("Full Name", placeholder="e.g. Priya Sharma")
        phone = st.text_input("Phone Number", placeholder="e.g. 9876543210")
        email = st.text_input("Email (Optional)", placeholder="e.g. priya@company.com")
        submitted = st.form_submit_button("➕ Add Customer", use_container_width=True, type="primary")

        if submitted:
            if not name or not phone:
                st.error("Name and phone are required.", icon="🚨")
            else:
                result = cust_logic.add_customer(name, phone, email)
                if result.startswith("Success"):
                    st.session_state.toast_msg = result
                    st.rerun()
                else:
                    st.error(result, icon="🚨")

# ── SEARCH & HISTORY ──
with tab_search:
    st.markdown('<div class="section-header">Customer Lookup</div>', unsafe_allow_html=True)
    lookup_phone = st.text_input("Enter Phone Number", key="lookup_phone", placeholder="e.g. 9876543210")

    if st.button("🔍 Search", use_container_width=True, type="primary"):
        if not lookup_phone:
            st.error("Please enter a phone number.", icon="🚨")
        else:
            with st.spinner("Looking up customer…"):
                result = cust_logic.find_customer_by_phone(lookup_phone)

            if result is None:
                st.warning(f"No customer found with phone: {lookup_phone}", icon="⚠️")
            elif isinstance(result, str):
                st.error(result, icon="🚨")
            else:
                # Customer profile card
                total_spent = sum(s.get('total_amount', 0) for s in result.get('sales', []))
                num_purchases = len(result.get('sales', []))

                pc1, pc2, pc3 = st.columns(3)
                with pc1: st.markdown(kpi_card("Customer", result['name'], "👤", "purple"), unsafe_allow_html=True)
                with pc2: st.markdown(kpi_card("Total Spent", f"₹{total_spent:,.0f}", "💰", "green"), unsafe_allow_html=True)
                with pc3: st.markdown(kpi_card("Purchases", str(num_purchases), "🛒", "blue"), unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Contact info
                st.markdown(f"📞 **Phone:** {result['phone']} &nbsp;&nbsp; 📧 **Email:** {result.get('email') or '—'}")

                # Purchase history
                if result.get('sales'):
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown('<div class="section-header">Purchase History</div>', unsafe_allow_html=True)
                    for s in result['sales']:
                        sale_date = s.get('sale_date', 'N/A')[:10]
                        with st.expander(f"🧾 Sale on {sale_date} — ₹{s['total_amount']:,.2f}"):
                            if s.get('items'):
                                for item in s['items']:
                                    product = item.get('products', {})
                                    st.markdown(f"• **{product.get('name', 'Unknown')}** ({product.get('sku', 'N/A')}) — {item['quantity']} × ₹{item['price_per_unit']:,.2f}")
                            else:
                                st.caption("No item details available.")
                else:
                    st.info("No purchase history yet.", icon="📋")

# ── UPDATE CUSTOMER ──
with tab_update:
    st.markdown('<div class="section-header">Update Customer</div>', unsafe_allow_html=True)
    with st.form("update_customer_form"):
        if customer_list:
            cust_options = {f"{c['name']} ({c['phone']})": c['phone'] for c in customer_list}
            selected = st.selectbox("Select Customer", list(cust_options.keys()))
            selected_phone = cust_options[selected]
            current = next((c for c in customer_list if c['phone'] == selected_phone), None)

            if current:
                st.info(f"Editing: **{current['name']}** — {current['phone']}", icon="✏️")
                new_name = st.text_input("New Name", value=current['name'], key="uc_name")
                new_phone = st.text_input("New Phone", value=current['phone'], key="uc_phone")
                new_email = st.text_input("New Email", value=current.get('email') or '', key="uc_email")
                submitted = st.form_submit_button("✏️ Update Customer", use_container_width=True, type="primary")

                if submitted:
                    updates = {"name": new_name.strip(), "phone": new_phone.strip(), "email": new_email.strip() or None}
                    result = cust_logic.update_customer(selected_phone, updates)
                    if result.startswith("Success"):
                        st.session_state.toast_msg = result
                        st.rerun()
                    else:
                        st.error(result, icon="🚨")
        else:
            st.info("No customers available to update.", icon="👥")
            st.form_submit_button("Update", disabled=True)

# ── DELETE CUSTOMER ──
with tab_delete:
    st.markdown('<div class="section-header">Delete Customer</div>', unsafe_allow_html=True)
    st.warning("⚠️ **Caution**: Deleting a customer is permanent. Their sales records will remain but will no longer be linked.", icon="⚠️")

    with st.form("delete_customer_form"):
        if customer_list:
            cust_options = {f"{c['name']} ({c['phone']})": c['phone'] for c in customer_list}
            selected = st.selectbox("Select Customer to Delete", list(cust_options.keys()), key="dc_select")
            selected_phone = cust_options[selected]
            current = next((c for c in customer_list if c['phone'] == selected_phone), None)
            if current:
                st.error(f"You are about to delete: **{current['name']}** ({current['phone']})", icon="🗑️")
            confirm = st.text_input("Type the phone number to confirm", key="dc_confirm", placeholder=f"Type '{selected_phone}' to confirm")
            submitted = st.form_submit_button("🗑️ Delete Customer Permanently", use_container_width=True, type="primary")

            if submitted:
                if confirm.strip() != selected_phone:
                    st.error(f"Phone confirmation does not match. Expected: {selected_phone}", icon="🚨")
                else:
                    result = cust_logic.delete_customer_by_phone(selected_phone)
                    if result.startswith("Success"):
                        st.session_state.toast_msg = result
                        st.rerun()
                    else:
                        st.error(result, icon="🚨")
        else:
            st.info("No customers available to delete.", icon="👥")
            st.form_submit_button("Delete", disabled=True)
