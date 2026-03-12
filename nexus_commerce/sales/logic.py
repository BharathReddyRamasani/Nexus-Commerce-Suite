"""
Nexus Commerce Suite — Sales Logic
=====================================
Core transaction processing: validation, recording, and stock updates.
"""
import logging
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
    total_profit = 0
    low_stock_alerts = []

    try:
        # ── PHASE 1: VALIDATION ──
        logger.info("Processing sale with %d item(s), %d payment(s)", len(items), len(payments))

        product_details = {}
        for item in items:
            sku = item['sku'].strip().upper()
            sale_quantity = item['quantity']

            product_res = supabase.table("products").select("*").eq("sku", sku).maybe_single().execute()
            if not product_res.data:
                return {"success": False, "message": f"Product with SKU '{sku}' not found.", "alerts": []}

            product = product_res.data

            if product['quantity_on_hand'] < sale_quantity:
                msg = (f"Insufficient stock for {product['name']} (SKU: {sku}). "
                       f"Available: {product['quantity_on_hand']}, Requested: {sale_quantity}.")
                return {"success": False, "message": msg, "alerts": []}

            product_details[sku] = product
            total_amount += product['selling_price'] * sale_quantity
            total_profit += (product['selling_price'] - product['cost_price']) * sale_quantity

        # Validate payment
        paid_amount = sum(p['amount'] for p in payments)
        if abs(paid_amount - total_amount) > 0.01:
            msg = f"Payment mismatch. Sale total: ₹{total_amount:.2f}, Paid: ₹{paid_amount:.2f}."
            return {"success": False, "message": msg, "alerts": []}

        # Validate customer
        customer_id = None
        if customer_phone:
            customer_res = supabase.table("customers").select("id").eq("phone", customer_phone.strip()).maybe_single().execute()
            if not customer_res.data:
                return {"success": False, "message": f"Customer with phone '{customer_phone}' not found.", "alerts": []}
            customer_id = customer_res.data['id']

        # ── PHASE 2: EXECUTION ──
        logger.info("Validation passed. Writing sale (₹%.2f, profit ₹%.2f)", total_amount, total_profit)

        # 1. Insert sale record
        sale_insert_res = supabase.table("sales").insert({
            "customer_id": customer_id,
            "total_amount": total_amount,
            "total_profit": total_profit
        }).execute()
        sale_id = sale_insert_res.data[0]['id']

        # 2. Insert line items and update stock
        for item in items:
            sku = item['sku'].strip().upper()
            product = product_details[sku]

            supabase.table("sale_items").insert({
                "sale_id": sale_id,
                "product_id": product['id'],
                "quantity": item['quantity'],
                "price_per_unit": product['selling_price']
            }).execute()

            new_quantity = product['quantity_on_hand'] - item['quantity']
            supabase.table("products").update({
                "quantity_on_hand": new_quantity,
                "last_sale_date": "now()"
            }).eq("sku", sku).execute()

            if new_quantity < 5:
                low_stock_alerts.append(f"⚠️ '{product['name']}' ({sku}) stock critically low ({new_quantity} remaining)")

        # 3. Insert payments
        for payment in payments:
            supabase.table("payments").insert({
                "sale_id": sale_id,
                "payment_method": payment['method'],
                "amount": payment['amount']
            }).execute()

        logger.info("Sale #%s recorded successfully.", sale_id[:8])
        return {"success": True, "message": f"Sale #{sale_id[:8]} recorded successfully!", "alerts": low_stock_alerts}

    except Exception as e:
        logger.error("Sale processing failed: %s", e)
        return {
            "success": False,
            "message": f"An error occurred during the sale. Please verify manually. Details: {e}",
            "alerts": []
        }
