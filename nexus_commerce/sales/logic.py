from ..common.supabase_client import get_supabase_client

def record_sale(items, payments, customer_phone=None):
    """
    Records a new sale, updates inventory, and logs payments.
    Always returns a dictionary with 'success' (bool), 'message' (str), and 'alerts' (list).
    """
    supabase = get_supabase_client()
    
    total_amount = 0
    total_profit = 0
    low_stock_alerts = []

    try:
        product_details = {}
        for item in items:
            sku = item['sku'].upper()
            sale_quantity = item['quantity']
            
            product_res = supabase.table("products").select("*").eq("sku", sku).single().execute()
            if not product_res.data:
                return {"success": False, "message": f"Error: Product with SKU '{sku}' not found.", "alerts": []}
            
            product = product_res.data
            if product['quantity_on_hand'] < sale_quantity:
                message = f"Error: Insufficient stock for {product['name']} (SKU: {sku}). Available: {product['quantity_on_hand']}, Requested: {sale_quantity}."
                return {"success": False, "message": message, "alerts": []}
            
            product_details[sku] = product
            total_amount += product['selling_price'] * sale_quantity
            total_profit += (product['selling_price'] - product['cost_price']) * sale_quantity
        
        paid_amount = sum(p['amount'] for p in payments)
        if paid_amount != total_amount:
            message = f"Error: Payment mismatch. Sale total is Rs. {total_amount:.2f}, but payment received is Rs. {paid_amount:.2f}."
            return {"success": False, "message": message, "alerts": []}

        customer_id = None
        if customer_phone:
            customer_res = supabase.table("customers").select("id").eq("phone", customer_phone).single().execute()
            if not customer_res.data:
                return {"success": False, "message": f"Error: Customer with phone number '{customer_phone}' not found.", "alerts": []}
            customer_id = customer_res.data['id']

        sale_insert_res = supabase.table("sales").insert({
            "customer_id": customer_id,
            "total_amount": total_amount,
            "total_profit": total_profit
        }).execute()
        sale_id = sale_insert_res.data[0]['id']

        for item in items:
            sku = item['sku'].upper()
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
                low_stock_alerts.append(f"Stock for '{product['name']}' ({sku}) is critically low ({new_quantity})!")

        for payment in payments:
            supabase.table("payments").insert({
                "sale_id": sale_id,
                "payment_method": payment['method'],
                "amount": payment['amount']
            }).execute()

        return {"success": True, "message": f"Sale #{sale_id[:8]} recorded successfully!", "alerts": low_stock_alerts}

    except Exception as e:
        message = f"An unexpected error occurred. Please verify the sale manually. Details: {e}"
        return {"success": False, "message": message, "alerts": []}

