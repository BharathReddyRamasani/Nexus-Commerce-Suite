from ..common.supabase_client import get_supabase_client
def add_product(name, sku, cost_price, selling_price, quantity_on_hand):
    """Adds a new product to the database."""
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
        if hasattr(response, 'error') and response.error:
             raise Exception(response.error.message)
        return f"Success: Product '{name}' added."
    except Exception as e:
        if 'unique constraint' in str(e).lower():
            return f"Error: A product with SKU '{sku.upper()}' already exists."
        return f"Error: Could not add product. Details: {e}"

def get_all_products():
    """Retrieves all products from the database."""
    supabase = get_supabase_client()
    try:
        response = supabase.table("products").select("*").order("name").execute()
        return response.data
    except Exception as e:
        return f"Error: Could not fetch products. Details: {e}"

def find_product_by_sku(sku):
    """Finds a single product by its SKU."""
    supabase = get_supabase_client()
    try:
        response = supabase.table("products").select("*").eq("sku", sku.upper()).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        return f"Error: Could not find product. Details: {e}"

def update_product_by_sku(sku, updates):
    """Updates a product's details (like name and price) in the database."""
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
    Adjusts the stock for a product and creates an audit trail record.
    """
    supabase = get_supabase_client()
    try:
        product_res = supabase.table("products").select("id, quantity_on_hand").eq("sku", sku.upper()).single().execute()
        if not product_res.data:
            return f"Error: Product with SKU '{sku.upper()}' not found."
        
        product = product_res.data
        current_quantity = product['quantity_on_hand']
        new_quantity = current_quantity + change_quantity

        if new_quantity < 0:
            return f"Error: Adjustment would result in negative stock ({new_quantity})."

        adjustment_data = {
            "product_id": product['id'],
            "change_quantity": change_quantity,
            "reason": reason
        }
        supabase.table("stock_adjustments").insert(adjustment_data).execute()

        supabase.table("products").update({"quantity_on_hand": new_quantity}).eq("sku", sku.upper()).execute()

        return f"Success: Stock for SKU '{sku.upper()}' adjusted to {new_quantity}."
    except Exception as e:
        return f"Error: Could not adjust stock. Details: {e}"

