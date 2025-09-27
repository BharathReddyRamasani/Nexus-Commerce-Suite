from datetime import datetime, timedelta
from ..common.supabase_client import get_supabase_client
# This import is a key part of the modular design, allowing this module
# to reuse the functionality of the inventory module to get product data.
from ..inventory.logic import find_product_by_sku

def get_profit_report(period):
    """
    Generates a profit and revenue report for a given period (daily, weekly, monthly).
    Returns a dictionary containing the results or an error message.
    """
    supabase = get_supabase_client()
    
    end_date = datetime.now()
    if period == 'daily':
        start_date = end_date - timedelta(days=1)
    elif period == 'weekly':
        start_date = end_date - timedelta(weeks=7) # Corrected to weeks=1
    elif period == 'monthly':
        # Using 30 days provides a consistent "monthly" window.
        start_date = end_date - timedelta(days=30)
    else:
        return {"error": "Invalid period specified."}

    try:
        # Query the sales table for records within the calculated date range.
        response = supabase.table("sales").select("total_amount, total_profit").gte("sale_date", start_date.isoformat()).lte("sale_date", end_date.isoformat()).execute()
        
        if hasattr(response, 'error') and response.error:
            raise Exception(response.error.message)

        # Calculate the totals by summing the values from the fetched data.
        total_revenue = sum(sale['total_amount'] for sale in response.data)
        total_profit = sum(sale['total_profit'] for sale in response.data)
        
        return {"total_revenue": total_revenue, "total_profit": total_profit, "start_date": start_date, "end_date": end_date}
    except Exception as e:
        return {"error": f"Could not generate profit report. Details: {e}"}

def get_product_health_report():
    """
    Generates a report on the health status of all products based on their last sale date.
    Returns a dictionary containing the report data or an error message.
    """
    supabase = get_supabase_client()
    try:
        response = supabase.table("products").select("sku, name, quantity_on_hand, last_sale_date").execute()
        
        if hasattr(response, 'error') and response.error:
            raise Exception(response.error.message)

        report_data = []
        now = datetime.now()
        for product in response.data:
            status = "Frozen" # Default status for products that have never been sold.
            if product.get('last_sale_date'):
                # Supabase returns dates in ISO format with timezone info.
                last_sale = datetime.fromisoformat(product['last_sale_date'])
                # We make the current time timezone-aware to match the stored format for an accurate comparison.
                days_since_sale = (now.astimezone() - last_sale).days
                
                if days_since_sale <= 30:
                    status = "Hot"
                elif days_since_sale <= 90:
                    status = "Cooling"
            
            report_data.append({
                "sku": product['sku'],
                "name": product['name'],
                "quantity": product['quantity_on_hand'],
                "status": status
            })
        
        # Return the data inside a dictionary for consistency with other functions.
        return {"data": sorted(report_data, key=lambda x: x['name'])}
    except Exception as e:
        return {"error": f"Could not generate product health report. Details: {e}"}

def get_payment_summary(period):
    """
    Generates a summary of payments by method for a given period.
    Returns a dictionary containing the summary or an error message.
    """
    supabase = get_supabase_client()
    
    end_date = datetime.now()
    if period == 'daily':
        start_date = end_date - timedelta(days=1)
    elif period == 'weekly':
        start_date = end_date - timedelta(weeks=7) # Corrected to weeks=1
    elif period == 'monthly':
        start_date = end_date - timedelta(days=30)
    else:
        return {"error": "Invalid period specified."}

    try:
        # First, we need to find all sales that occurred within the date range.
        sales_response = supabase.table("sales").select("id").gte("sale_date", start_date.isoformat()).lte("sale_date", end_date.isoformat()).execute()
        
        if not sales_response.data:
            return {"summary": {}, "start_date": start_date, "end_date": end_date}
            
        sale_ids = [sale['id'] for sale in sales_response.data]
        
        # Then, we fetch all payments linked to those sales.
        payments_response = supabase.table("payments").select("payment_method, amount").in_("sale_id", sale_ids).execute()
        
        summary = {}
        for payment in payments_response.data:
            method = payment['payment_method']
            amount = payment['amount']
            # Aggregate the amounts for each payment method.
            summary[method] = summary.get(method, 0) + amount
            
        return {"summary": summary, "start_date": start_date, "end_date": end_date}
    except Exception as e:
        return {"error": f"Could not generate payment summary. Details: {e}"}

def simulate_sale(discount_percentage, skus):
    """
    Simulates the financial impact of a discount on a list of products.
    Returns a dictionary containing the simulation results.
    """
    simulation_results = []
    for sku in skus:
        # Reuses the logic from the inventory module to find product details.
        product = find_product_by_sku(sku)
        
        if not isinstance(product, dict):
            # If the product isn't found, create an error entry for the report.
            simulation_results.append({"sku": sku, "error": f"Product with SKU '{sku}' not found."})
            continue

        # Perform the financial calculations.
        original_price = product['selling_price']
        cost_price = product['cost_price']
        original_profit = original_price - cost_price

        discounted_price = original_price * (1 - discount_percentage / 100)
        new_profit = discounted_price - cost_price

        simulation_results.append({
            "name": product['name'],
            "sku": product['sku'],
            "original_price": original_price,
            "discounted_price": discounted_price,
            "original_profit": original_profit,
            "new_profit": new_profit,
        })
        
    return {"data": simulation_results}

def get_sales_over_time(days=30):
    """
    Retrieves sales data for the last N days to power the dashboard chart.
    """
    supabase = get_supabase_client()
    try:
        start_date = datetime.now() - timedelta(days=days)
        response = supabase.table("sales").select("sale_date, total_amount").gte("sale_date", start_date.isoformat()).execute()

        if hasattr(response, 'error') and response.error:
            raise Exception(response.error.message)
            
        return {"data": response.data}
    except Exception as e:
        return {"error": f"Could not fetch sales data for the dashboard chart. Details: {e}"}

