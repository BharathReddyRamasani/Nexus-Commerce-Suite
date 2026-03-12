"""
Nexus Commerce Suite — Sales Logic
=====================================
Core transaction processing: validation, recording, and stock updates.
"""
import logging
import streamlit as st
from ..common.supabase_client import get_supabase_client

logger = logging.getLogger("nexus_commerce.sales")


def record_sale(items: list, payments: list, customer_phone: str = None) -> dict:
    """
    Record a complete sale transaction.
    Validates stock and payment, then writes sale, items, payments, and updates inventory.
    Returns: {'success': bool, 'message': str, 'alerts': list}
    """
    supabase = get_supabase_client()

    total_amount = 0
    total_tax = 0
    total_profit = 0
    low_stock_alerts = []

    try:
        # ── PHASE 1: VALIDATION ──
        logger.info("Processing sale with %d item(s), %d payment(s)", len(items), len(payments))

        product_details = {}
        for item in items:
            sku = item['sku'].strip().upper()
            sale_quantity = item['quantity']

            product_res = supabase.table("products").select("*") \
                .eq("sku", sku) \
                .eq("user_id", st.session_state.get("user_id")) \
                .maybe_single().execute()
            if not product_res.data:
                return {"success": False, "message": f"Product with SKU '{sku}' not found.", "alerts": []}

            product = product_res.data

            if product['quantity_on_hand'] < sale_quantity:
                msg = (f"Insufficient stock for {product['name']} (SKU: {sku}). "
                       f"Available: {product['quantity_on_hand']}, Requested: {sale_quantity}.")
                return {"success": False, "message": msg, "alerts": []}

            product_details[sku] = product
            product_details[sku] = product
            item_revenue = product['selling_price'] * sale_quantity
            item_tax = item_revenue * (product.get('tax_rate', 0) / 100.0)
            
            total_amount += item_revenue + item_tax
            total_tax += item_tax
            total_profit += (product['selling_price'] - product['cost_price']) * sale_quantity

        # Validate payment
        paid_amount = sum(p['amount'] for p in payments)
        if abs(paid_amount - total_amount) > 0.01:
            msg = f"Payment mismatch. Sale total: ₹{total_amount:.2f}, Paid: ₹{paid_amount:.2f}."
            return {"success": False, "message": msg, "alerts": []}

        # Validate customer
        customer_id = None
        if customer_phone:
            customer_res = supabase.table("customers").select("id") \
                .eq("phone", customer_phone.strip()) \
                .eq("user_id", st.session_state.get("user_id")) \
                .maybe_single().execute()
            if not customer_res.data:
                return {"success": False, "message": f"Customer with phone '{customer_phone}' not found.", "alerts": []}
            customer_id = customer_res.data['id']

        # ── PHASE 2: EXECUTION ──
        logger.info("Validation passed. Writing sale (₹%.2f, profit ₹%.2f)", total_amount, total_profit)

        sale_insert_res = supabase.table("sales").insert({
            "customer_id": customer_id,
            "total_amount": total_amount,
            "total_tax": total_tax,
            "total_profit": total_profit,
            "user_id": st.session_state.get("user_id")
        }).execute()
        sale_id = sale_insert_res.data[0]['id']

        for item in items:
            sku = item['sku'].strip().upper()
            product = product_details[sku]

            supabase.table("sale_items").insert({
                "sale_id": sale_id,
                "product_id": product['id'],
                "quantity": item['quantity'],
                "price_per_unit": product['selling_price'],
                "tax_amount": (product['selling_price'] * item['quantity']) * (product.get('tax_rate', 0) / 100.0),
                "user_id": st.session_state.get("user_id")
            }).execute()

            new_quantity = product['quantity_on_hand'] - item['quantity']
            supabase.table("products").update({
                "quantity_on_hand": new_quantity,
                "last_sale_date": "now()"
            }).eq("sku", sku).eq("user_id", st.session_state.get("user_id")).execute()

            if new_quantity < 5:
                low_stock_alerts.append(f"⚠️ '{product['name']}' ({sku}) stock critically low ({new_quantity} remaining)")

        # 3. Insert payments
        for payment in payments:
            supabase.table("payments").insert({
                "sale_id": sale_id,
                "payment_method": payment['method'],
                "amount": payment['amount'],
                "user_id": st.session_state.get("user_id")
            }).execute()

        return {"success": True, "message": f"Sale #{sale_id[:8]} recorded successfully!", "alerts": low_stock_alerts}

    except Exception as e:
        logger.error("Sale processing failed: %s", e)
        return {
            "success": False,
            "message": f"An error occurred during the sale. Please verify manually. Details: {e}",
            "alerts": []
        }


def process_return(sale_id: str, product_sku: str, quantity: int, reason: str = "") -> dict:
    """Process a product return: restock item, record return, and adjust financials."""
    supabase = get_supabase_client()
    try:
        # 1. Get product details
        product_res = supabase.table("products").select("id, name, quantity_on_hand, selling_price, tax_rate, cost_price") \
            .eq("sku", product_sku.upper()) \
            .eq("user_id", st.session_state.get("user_id")) \
            .maybe_single().execute()
        if not product_res.data:
            return {"success": False, "message": "Product not found."}
        product = product_res.data

        # 2. Get sale item details
        item_res = supabase.table("sale_items").select("*") \
            .eq("sale_id", sale_id) \
            .eq("product_id", product['id']) \
            .eq("user_id", st.session_state.get("user_id")) \
            .maybe_single().execute()
        if not item_res.data:
            return {"success": False, "message": "This product was not found in the original sale."}
        
        sale_item = item_res.data
        if quantity > sale_item['quantity']:
            return {"success": False, "message": f"Cannot return more than purchased ({sale_item['quantity']})."}

        # 3. Calculate refund
        unit_price = float(sale_item['price_per_unit'])
        unit_tax = unit_price * (product.get('tax_rate', 0) / 100.0)
        refund_amount = (unit_price + unit_tax) * quantity
        lost_profit = (unit_price - float(product['cost_price'])) * quantity

        # 4. Record Return
        supabase.table("returns").insert({
            "sale_id": sale_id,
            "product_id": product['id'],
            "quantity": quantity,
            "refund_amount": refund_amount,
            "reason": reason,
            "user_id": st.session_state.get("user_id")
        }).execute()

        # 5. Restock Product
        new_qty = product['quantity_on_hand'] + quantity
        supabase.table("products").update({"quantity_on_hand": new_qty}).eq("id", product['id']).execute()

        # 6. Adjust Sale Totals (Optional but recommended for consistency)
        sale_res = supabase.table("sales").select("*") \
            .eq("id", sale_id) \
            .eq("user_id", st.session_state.get("user_id")) \
            .maybe_single().execute()
        if sale_res.data:
            current_sale = sale_res.data
            supabase.table("sales").update({
                "total_amount": float(current_sale['total_amount']) - refund_amount,
                "total_profit": float(current_sale['total_profit']) - lost_profit,
                "total_tax": float(current_sale.get('total_tax', 0)) - (unit_tax * quantity)
            }).eq("id", sale_id).eq("user_id", st.session_state.get("user_id")).execute()

        logger.info("Processed return: Sale #%s, SKU: %s, Qty: %d", sale_id[:8], product_sku, quantity)
        return {"success": True, "message": f"Successfully processed return for {quantity} units of '{product['name']}'. Refunded ₹{refund_amount:,.2f}."}

    except Exception as e:
        logger.error("Return processing failed: %s", e)
        return {"success": False, "message": f"Error: {e}"}
