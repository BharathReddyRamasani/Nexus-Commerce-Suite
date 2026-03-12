"""
Nexus Commerce Suite — Reports & Analytics Logic
===================================================
Business intelligence: profit reports, product health, payment analysis, and sale simulation.
"""
import logging
from datetime import datetime, timedelta
from ..common.supabase_client import get_supabase_client
from ..inventory.logic import find_product_by_sku

logger = logging.getLogger("nexus_commerce.reports")


def _get_date_range(period: str):
    """Calculate start/end dates for the given period."""
    end_date = datetime.now()
    if period == 'daily':
        start_date = end_date - timedelta(days=1)
    elif period == 'weekly':
        start_date = end_date - timedelta(weeks=1)
    elif period == 'monthly':
        start_date = end_date - timedelta(days=30)
    else:
        return None, None
    return start_date, end_date


def get_profit_report(period: str) -> dict:
    """Generate a profit and revenue report for the given period."""
    supabase = get_supabase_client()

    start_date, end_date = _get_date_range(period)
    if start_date is None:
        return {"error": "Invalid period specified. Use 'daily', 'weekly', or 'monthly'."}

    try:
        logger.info("Generating profit report for period: %s", period)
        response = supabase.table("sales").select("total_amount, total_profit, total_tax") \
            .gte("sale_date", start_date.isoformat()) \
            .lte("sale_date", end_date.isoformat()).execute()

        if hasattr(response, 'error') and response.error:
            raise Exception(response.error.message)

        total_revenue = sum(sale['total_amount'] for sale in response.data)
        total_profit = sum(sale['total_profit'] for sale in response.data)
        total_tax = sum(sale.get('total_tax', 0) for sale in response.data)

        return {
            "total_revenue": total_revenue,
            "total_profit": total_profit,
            "total_tax": total_tax,
            "start_date": start_date,
            "end_date": end_date
        }
    except Exception as e:
        logger.error("Profit report failed: %s", e)
        return {"error": f"Could not generate profit report. Details: {e}"}


def get_product_health_report() -> dict:
    """Categorize products by sales velocity: Hot, Cooling, Frozen."""
    supabase = get_supabase_client()
    try:
        logger.info("Generating product health report")
        response = supabase.table("products").select("*").execute()

        if hasattr(response, 'error') and response.error:
            raise Exception(response.error.message)

        report_data = []
        now = datetime.now()
        for product in response.data:
            status = "Frozen"
            if product.get('last_sale_date'):
                last_sale = datetime.fromisoformat(product['last_sale_date'])
                days_since_sale = (now.astimezone() - last_sale).days

                if days_since_sale <= 30:
                    status = "Hot"
                elif days_since_sale <= 90:
                    status = "Cooling"

            report_data.append({
                "sku": product.get('sku', 'N/A'),
                "name": product.get('name', 'Unknown'),
                "quantity": product.get('quantity_on_hand', 0),
                "status": status
            })

        return {"data": sorted(report_data, key=lambda x: x['name'])}
    except Exception as e:
        logger.error("Product health report failed: %s", e)
        return {"error": f"Could not generate product health report. Details: {e}"}


def get_payment_summary(period: str) -> dict:
    """Summarize payments by method for the given period."""
    supabase = get_supabase_client()

    start_date, end_date = _get_date_range(period)
    if start_date is None:
        return {"error": "Invalid period specified."}

    try:
        logger.info("Generating payment summary for period: %s", period)
        sales_response = supabase.table("sales").select("id") \
            .gte("sale_date", start_date.isoformat()) \
            .lte("sale_date", end_date.isoformat()).execute()

        if not sales_response.data:
            return {"summary": {}, "start_date": start_date, "end_date": end_date}

        sale_ids = [sale['id'] for sale in sales_response.data]
        payments_response = supabase.table("payments").select("payment_method, amount").in_("sale_id", sale_ids).execute()

        summary = {}
        for payment in payments_response.data:
            method = payment['payment_method']
            summary[method] = summary.get(method, 0) + payment['amount']

        return {"summary": summary, "start_date": start_date, "end_date": end_date}
    except Exception as e:
        logger.error("Payment summary failed: %s", e)
        return {"error": f"Could not generate payment summary. Details: {e}"}


def simulate_sale(discount_percentage: float, skus: list) -> dict:
    """Simulate the financial impact of a discount on products."""
    logger.info("Running sale simulation: %.1f%% discount on %d SKU(s)", discount_percentage, len(skus))
    simulation_results = []

    for sku in skus:
        product = find_product_by_sku(sku)
        if not isinstance(product, dict):
            simulation_results.append({"sku": sku, "error": f"Product '{sku}' not found."})
            continue

        original_price = product['selling_price']
        cost_price = product['cost_price']
        original_profit = original_price - cost_price
        discounted_price = original_price * (1 - discount_percentage / 100)
        new_profit = discounted_price - cost_price

        simulation_results.append({
            "name": product['name'],
            "sku": product['sku'],
            "original_price": original_price,
            "discounted_price": round(discounted_price, 2),
            "original_profit": round(original_profit, 2),
            "new_profit": round(new_profit, 2),
        })

    return {"data": simulation_results}


def get_sales_over_time(days: int = 30) -> dict:
    """Retrieve daily sales data for the chart on the dashboard."""
    supabase = get_supabase_client()
    try:
        start_date = datetime.now() - timedelta(days=days)
        response = supabase.table("sales").select("sale_date, total_amount") \
            .gte("sale_date", start_date.isoformat()).execute()

        if hasattr(response, 'error') and response.error:
            raise Exception(response.error.message)

        return {"data": response.data}
    except Exception as e:
        logger.error("Failed to fetch sales over time: %s", e)
        return {"error": f"Could not fetch sales data. Details: {e}"}
