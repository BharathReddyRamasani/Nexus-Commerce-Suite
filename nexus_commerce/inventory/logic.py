from ..common.supabase_client import get_supabase_client

def add_product(name, sku, cost_price, selling_price, quantity_on_hand):
    """
    Adds a new product to the database.
    Returns a string indicating success or failure.
    """
    supabase = get_supabase_client()
    try:
        product_data = {
            "name": name,
            "sku": sku.upper(),
            "cost_price": cost_price,
            "selling_price": selling_price,
            "quantity_on_hand": quantity_on_hand,
        }
        response = supabase.table("products").insert(product_data).execute()
        
        # Robust error checking for the Supabase v2 client library
        if hasattr(response, 'error') and response.error:
             raise Exception(response.error.message)
             
        return f"Success: Product '{name}' added."
    except Exception as e:
        # Provide a more specific and user-friendly error for the most common issue
        if 'unique constraint' in str(e).lower() and 'sku' in str(e).lower():
            return f"Error: A product with the SKU '{sku.upper()}' already exists."
        return f"Error: Could not add product. Details: {e}"

def get_all_products():
    """
    Retrieves all products from the database, ordered by name.
    Returns a list of product dictionaries or an error string.
    """
    supabase = get_supabase_client()
    try:
        response = supabase.table("products").select("*").order("name").execute()
        return response.data
    except Exception as e:
        return f"Error: Could not fetch products. Details: {e}"

def find_product_by_sku(sku):
    """
    Finds a single product by its unique SKU.
    Returns a product dictionary if found, None if not found, or an error string.
    """
    supabase = get_supabase_client()
    try:
        # .maybe_single() is efficient as it expects at most one result
        response = supabase.table("products").select("*").eq("sku", sku.upper()).maybe_single().execute()
        return response.data
    except Exception as e:
        return f"Error: Could not find product. Details: {e}"

def update_product_by_sku(sku, updates):
    """

    Updates a product's non-stock details (like name and price) in the database.
    Returns a string indicating success or failure.
    """
    supabase = get_supabase_client()
    try:
        response = supabase.table("products").update(updates).eq("sku", sku.upper()).execute()
        if hasattr(response, 'error') and response.error:
             raise Exception(response.error.message)
        return f"Success: Product with SKU '{sku.upper()}' has been updated."
    except Exception as e:
        return f"Error: Could not update product. Details: {e}"

def adjust_stock_quantity(sku, change_quantity, reason):
    """
    Adjusts the stock for a product for auditing purposes (e.g., damage, correction)
    and creates a corresponding record in the stock_adjustments table.
    Returns a string indicating success or failure.
    """
    supabase = get_supabase_client()
    try:
        # Step 1: Find the product to get its ID and current quantity.
        product_res = supabase.table("products").select("id, quantity_on_hand").eq("sku", sku.upper()).maybe_single().execute()
        
        if not product_res.data:
            return f"Error: Product with SKU '{sku.upper()}' not found."
        
        product = product_res.data
        current_quantity = product['quantity_on_hand']
        new_quantity = current_quantity + change_quantity

        # Prevent stock from going below zero.
        if new_quantity < 0:
            return f"Error: Adjustment would result in negative stock ({new_quantity}). Current stock is {current_quantity}."

        # Step 2: Create the audit trail record in the stock_adjustments table.
        adjustment_data = {
            "product_id": product['id'],
            "change_quantity": change_quantity,
            "reason": reason
        }
        adj_response = supabase.table("stock_adjustments").insert(adjustment_data).execute()
        if hasattr(adj_response, 'error') and adj_response.error:
            raise Exception(f"Failed to create audit record: {adj_response.error.message}")

        # Step 3: If the audit record was successful, update the actual quantity in the products table.
        update_response = supabase.table("products").update({"quantity_on_hand": new_quantity}).eq("sku", sku.upper()).execute()
        if hasattr(update_response, 'error') and update_response.error:
            # This part is a failsafe, though unlikely to happen if the first steps succeed.
            raise Exception(f"Audit record created, but failed to update product stock: {update_response.error.message}")

        return f"Success: Stock for SKU '{sku.upper()}' adjusted from {current_quantity} to {new_quantity}."
    except Exception as e:
        return f"Error: Could not adjust stock. Details: {e}"

