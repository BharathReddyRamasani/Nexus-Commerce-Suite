from datetime import datetime, timedelta
from ..common.supabase_client import get_supabase_client

def get_profit_report(period):
    """Generates a profit and revenue report for a given period."""
    supabase = get_supabase_client()
    
    end_date = datetime.now()
    if period == 'daily':
        start_date = end_date - timedelta(days=1)
    elif period == 'weekly':
        start_date = end_date - timedelta(weeks=1)
    elif period == 'monthly':
        start_date = end_date - timedelta(days=30)
    else:
        return {"error": "Invalid period specified."}

    try:
        response = supabase.table("sales").select("total_amount, total_profit").gte("sale_date", start_date.isoformat()).lte("sale_date", end_date.isoformat()).execute()
        
        if hasattr(response, 'error') and response.error:
            raise Exception(response.error.message)

        total_revenue = sum(sale['total_amount'] for sale in response.data)
        total_profit = sum(sale['total_profit'] for sale in response.data)
        
        return {"total_revenue": total_revenue, "total_profit": total_profit, "start_date": start_date, "end_date": end_date}
    except Exception as e:
        return {"error": f"Could not generate report. Details: {e}"}

def get_product_health_report():
    """Generates a report on the health status of all products."""
    supabase = get_supabase_client()
    try:
        response = supabase.table("products").select("sku, name, quantity_on_hand, last_sale_date").execute()
        
        if hasattr(response, 'error') and response.error:
            raise Exception(response.error.message)

        report_data = []
        now = datetime.now()
        for product in response.data:
            status = "Frozen"
            if product.get('last_sale_date'):
                last_sale = datetime.fromisoformat(product['last_sale_date'])
                days_since_sale = (now - last_sale.replace(tzinfo=None)).days
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
        
        return {"data": sorted(report_data, key=lambda x: x['name'])}
    except Exception as e:
        return {"error": f"Could not generate report. Details: {e}"}

def get_payment_summary(period):
    """Generates a summary of payments by method for a given period."""
    supabase = get_supabase_client()
    
    end_date = datetime.now()
    if period == 'daily':
        start_date = end_date - timedelta(days=1)
    elif period == 'weekly':
        start_date = end_date - timedelta(weeks=1)
    elif period == 'monthly':
        start_date = end_date - timedelta(days=30)
    else:
        return {"error": "Invalid period specified."}

    try:
        sales_response = supabase.table("sales").select("id").gte("sale_date", start_date.isoformat()).lte("sale_date", end_date.isoformat()).execute()
        
        if not sales_response.data:
            return {"summary": {}, "start_date": start_date, "end_date": end_date}
            
        sale_ids = [sale['id'] for sale in sales_response.data]
        
        payments_response = supabase.table("payments").select("payment_method, amount").in_("sale_id", sale_ids).execute()
        
        summary = {}
        for payment in payments_response.data:
            method = payment['payment_method']
            amount = payment['amount']
            summary[method] = summary.get(method, 0) + amount
            
        return {"summary": summary, "start_date": start_date, "end_date": end_date}
    except Exception as e:
        return {"error": f"Could not generate report. Details: {e}"}

