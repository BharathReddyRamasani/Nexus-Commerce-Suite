"""
Nexus Commerce Suite — Inventory Logic
========================================
CRUD operations and stock management for products.
"""
import logging
from ..common.supabase_client import get_supabase_client

logger = logging.getLogger("nexus_commerce.inventory")


def get_categories() -> list:
    """Retrieve all product categories."""
    supabase = get_supabase_client()
    try:
        response = supabase.table("categories").select("*").order("name").execute()
        return response.data
    except Exception as e:
        logger.error("Failed to fetch categories: %s", e)
        return []

def get_brands() -> list:
    """Retrieve all brands."""
    supabase = get_supabase_client()
    try:
        response = supabase.table("brands").select("*").order("name").execute()
        return response.data
    except Exception as e:
        logger.error("Failed to fetch brands: %s", e)
        return []

def add_product(sku: str, name: str, cost: float, sell: float, qty: int = 0, desc: str = "", category_id: str = None, brand_id: str = None, tax_rate: float = 0.0) -> str:
    """Add a new product to the inventory. Returns a success/error message string."""
    supabase = get_supabase_client()
    try:
        product_data = {
            "name": name.strip(),
            "sku": sku.strip().upper(),
            "cost_price": cost,
            "selling_price": sell,
            "tax_rate": tax_rate,
            "quantity_on_hand": qty,
            "description": desc,
            "category_id": category_id,
            "brand_id": brand_id
        }
        logger.info("Adding product: %s (SKU: %s)", name, sku.upper())
        response = supabase.table("products").insert(product_data).execute()

        if hasattr(response, 'error') and response.error:
            raise Exception(response.error.message)

        logger.info("Product '%s' added successfully.", name)
        return f"Success: Product '{name}' added."
    except Exception as e:
        if 'unique constraint' in str(e).lower() and 'sku' in str(e).lower():
            return f"Error: A product with the SKU '{sku.upper()}' already exists."
        logger.error("Failed to add product '%s': %s", name, e)
        return f"Error: Could not add product. Details: {e}"


def get_all_products() -> list | str:
    """Retrieve all products ordered by name. Returns list or error string."""
    supabase = get_supabase_client()
    try:
        # Use OR to include True and NULL (for rows created before schema migration)
        response = supabase.table("products").select("*").or_("is_active.eq.true,is_active.is.null").order("name").execute()
        return response.data
    except Exception as e:
        logger.error("Failed to fetch products: %s", e)
        return f"Error: Could not fetch products. Details: {e}"


def find_product_by_sku(sku: str) -> dict | None | str:
    """Find a product by SKU. Returns dict if found, None if not, or error string."""
    supabase = get_supabase_client()
    try:
        response = supabase.table("products").select("*").eq("sku", sku.strip().upper()).maybe_single().execute()
        return response.data
    except Exception as e:
        logger.error("Failed to find product SKU '%s': %s", sku, e)
        return f"Error: Could not find product. Details: {e}"


def update_product_by_sku(sku: str, updates: dict) -> str:
    """Update product details by SKU. Returns success/error message."""
    supabase = get_supabase_client()
    try:
        logger.info("Updating product SKU '%s' with: %s", sku.upper(), updates)
        response = supabase.table("products").update(updates).eq("sku", sku.strip().upper()).execute()
        if hasattr(response, 'error') and response.error:
            raise Exception(response.error.message)
        logger.info("Product SKU '%s' updated.", sku.upper())
        return f"Success: Product with SKU '{sku.upper()}' has been updated."
    except Exception as e:
        logger.error("Failed to update SKU '%s': %s", sku, e)
        return f"Error: Could not update product. Details: {e}"


def adjust_stock_quantity(sku: str, change_quantity: int, reason: str) -> str:
    """
    Adjust stock with an audit trail. Creates a record in stock_adjustments.
    Returns success/error message.
    """
    supabase = get_supabase_client()
    try:
        sku_upper = sku.strip().upper()
        logger.info("Stock adjustment request: SKU=%s, change=%d, reason='%s'", sku_upper, change_quantity, reason)

        # Step 1: Find product
        product_res = supabase.table("products").select("id, quantity_on_hand").eq("sku", sku_upper).maybe_single().execute()
        if not product_res.data:
            return f"Error: Product with SKU '{sku_upper}' not found."

        product = product_res.data
        current_qty = product['quantity_on_hand']
        new_qty = current_qty + change_quantity

        if new_qty < 0:
            return f"Error: Adjustment would result in negative stock ({new_qty}). Current stock is {current_qty}."

        # Step 2: Audit trail
        adj_response = supabase.table("stock_adjustments").insert({
            "product_id": product['id'],
            "change_quantity": change_quantity,
            "reason": reason.strip()
        }).execute()
        if hasattr(adj_response, 'error') and adj_response.error:
            raise Exception(f"Failed to create audit record: {adj_response.error.message}")

        # Step 3: Update stock
        update_response = supabase.table("products").update({"quantity_on_hand": new_qty}).eq("sku", sku_upper).execute()
        if hasattr(update_response, 'error') and update_response.error:
            raise Exception(f"Audit record created, but stock update failed: {update_response.error.message}")

        logger.info("Stock adjusted: SKU=%s, %d → %d", sku_upper, current_qty, new_qty)
        return f"Success: Stock for SKU '{sku_upper}' adjusted from {current_qty} to {new_qty}."
    except Exception as e:
        logger.error("Stock adjustment failed for SKU '%s': %s", sku, e)
        return f"Error: Could not adjust stock. Details: {e}"


def delete_product_by_sku(sku: str) -> str:
    """Delete a product by SKU. Returns success/error message."""
    supabase = get_supabase_client()
    try:
        sku_upper = sku.strip().upper()
        logger.info("Deleting product SKU: %s", sku_upper)

        # Check if product exists
        product_res = supabase.table("products").select("id, name").eq("sku", sku_upper).maybe_single().execute()
        if not product_res.data:
            return f"Error: Product with SKU '{sku_upper}' not found."

        product_name = product_res.data['name']

        # Soft Delete: Update is_active to False instead of deleting
        response = supabase.table("products").update({"is_active": False}).eq("sku", sku_upper).execute()
        if hasattr(response, 'error') and response.error:
            raise Exception(response.error.message)

        logger.info("Product '%s' (SKU: %s) soft-deleted.", product_name, sku_upper)
        return f"Success: Product '{product_name}' (SKU: {sku_upper}) has been removed from active inventory."
    except Exception as e:
        if 'violates foreign key' in str(e).lower():
            return f"Error: Cannot delete — this product has sales records linked to it."
        logger.error("Failed to delete SKU '%s': %s", sku, e)
        return f"Error: Could not delete product. Details: {e}"


def get_inventory_summary() -> dict:
    """Get inventory summary: total value, potential profit, counts by status."""
    supabase = get_supabase_client()
    try:
        response = supabase.table("products").select("cost_price, selling_price, quantity_on_hand").or_("is_active.eq.true,is_active.is.null").execute()
        if not response.data:
            return {"total_cost_value": 0, "total_sell_value": 0, "potential_profit": 0, "total_units": 0}

        total_cost = sum(p['cost_price'] * p['quantity_on_hand'] for p in response.data)
        total_sell = sum(p['selling_price'] * p['quantity_on_hand'] for p in response.data)
        total_units = sum(p['quantity_on_hand'] for p in response.data)

        return {
            "total_cost_value": round(total_cost, 2),
            "total_sell_value": round(total_sell, 2),
            "potential_profit": round(total_sell - total_cost, 2),
            "total_units": total_units
        }
    except Exception as e:
        logger.error("Inventory summary failed: %s", e)
        return {"error": str(e)}
