from ..common.supabase_client import get_supabase_client

def record_sale(items, payments, customer_phone=None):
    """
    Records a new sale, updates inventory, and logs payments.
    This is the most critical transactional function in the application.
    It always returns a dictionary with 'success' (bool), 'message' (str), and 'alerts' (list).
    """
    supabase = get_supabase_client()
    
    total_amount = 0
    total_profit = 0
    low_stock_alerts = []

    try:
        # --- PHASE 1: VALIDATION ---
        # Before writing anything to the database, we check everything.
        
        product_details = {}
        for item in items:
            sku = item['sku'].upper()
            sale_quantity = item['quantity']
            
            # Check if the product exists
            product_res = supabase.table("products").select("*").eq("sku", sku).maybe_single().execute()
            if not product_res.data:
                return {"success": False, "message": f"Validation Error: Product with SKU '{sku}' not found.", "alerts": []}
            
            product = product_res.data
            
            # Check if there is enough stock
            if product['quantity_on_hand'] < sale_quantity:
                message = f"Validation Error: Insufficient stock for {product['name']} (SKU: {sku}). Available: {product['quantity_on_hand']}, Requested: {sale_quantity}."
                return {"success": False, "message": message, "alerts": []}
            
            # Store details and calculate running totals
            product_details[sku] = product
            total_amount += product['selling_price'] * sale_quantity
            total_profit += (product['selling_price'] - product['cost_price']) * sale_quantity
        
        # Validate that the payment amount matches the sale total
        paid_amount = sum(p['amount'] for p in payments)
        # Use a small tolerance for floating point comparisons
        if abs(paid_amount - total_amount) > 0.01:
            message = f"Validation Error: Payment mismatch. Sale total is Rs. {total_amount:.2f}, but payment received is Rs. {paid_amount:.2f}."
            return {"success": False, "message": message, "alerts": []}

        # Validate the customer if a phone number was provided
        customer_id = None
        if customer_phone:
            customer_res = supabase.table("customers").select("id").eq("phone", customer_phone).maybe_single().execute()
            if not customer_res.data:
                return {"success": False, "message": f"Validation Error: Customer with phone number '{customer_phone}' not found.", "alerts": []}
            customer_id = customer_res.data['id']

        # --- PHASE 2: EXECUTION (Database Writes) ---
        # Note: The Supabase REST API does not support true atomic transactions across
        # multiple tables. This is a "best-effort" sequential write.

        # 1. Insert the main sale record
        sale_insert_res = supabase.table("sales").insert({
            "customer_id": customer_id,
            "total_amount": total_amount,
            "total_profit": total_profit
        }).execute()
        sale_id = sale_insert_res.data[0]['id']

        # 2. Insert each line item and update product stock
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
                "last_sale_date": "now()" # Update the timestamp for the health report
            }).eq("sku", sku).execute()
            
            # Check for low stock and add to alerts list
            if new_quantity < 5:
                low_stock_alerts.append(f"Stock for '{product['name']}' ({sku}) is now critically low ({new_quantity})!")

        # 3. Insert payment records
        for payment in payments:
            supabase.table("payments").insert({
                "sale_id": sale_id,
                "payment_method": payment['method'],
                "amount": payment['amount']
            }).execute()

        # If all steps complete, return a success dictionary
        return {"success": True, "message": f"Sale #{sale_id[:8]} recorded successfully!", "alerts": low_stock_alerts}

    except Exception as e:
        # Catch any unexpected errors during the process
        message = f"An unexpected error occurred during the sale process. Please verify the sale and stock levels manually. Details: {e}"
        return {"success": False, "message": message, "alerts": []}

