import click
from tabulate import tabulate
from . import logic

def profit_report_flow():
    """Interactive flow for the profit and revenue report."""
    click.secho("\n--- Profit & Revenue Report ---", fg="blue", bold=True)
    period = click.prompt("Select period (daily, weekly, monthly)", type=click.Choice(['daily', 'weekly', 'monthly']), default='daily')
    
    # Receives a single dictionary named 'response'.
    response = logic.get_profit_report(period)
    
    # Checks for the 'error' key inside the dictionary to handle failures.
    if "error" in response:
        click.secho(response["error"], fg="red")
        return

    start_date = response['start_date'].strftime('%d %b %Y')
    end_date = response['end_date'].strftime('%d %b %Y')
    
    click.secho(f"\nReport for period: {start_date} to {end_date}", fg="cyan")
    headers = ["Metric", "Amount"]
    table_data = [
        ["Total Revenue", f"Rs. {response['total_revenue']:.2f}"],
        ["Total Profit", f"Rs. {response['total_profit']:.2f}"],
    ]
    click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))

def product_health_report_flow():
    """Flow for the product health status report."""
    click.secho("\n--- Product Health Status ---", fg="blue", bold=True)
    
    response = logic.get_product_health_report()
    
    if "error" in response:
        click.secho(response["error"], fg="red")
        return

    products = response.get("data", [])
    if not products:
        click.secho("No products found to report on.", fg="yellow")
        return
        
    headers = ["SKU", "Name", "Qty", "Status"]
    table_data = []
    for p in products:
        # Assign colors based on status for better visual feedback
        status_color = "green" if p['status'] == 'Hot' else "yellow" if p['status'] == 'Cooling' else "red"
        status_text = click.style(p['status'], fg=status_color)
        table_data.append([p['sku'], p['name'], p['quantity'], status_text])
        
    click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))

def payment_summary_flow():
    """Flow for the payment methods summary report."""
    click.secho("\n--- Payment Methods Summary ---", fg="blue", bold=True)
    period = click.prompt("Select period (daily, weekly, monthly)", type=click.Choice(['daily', 'weekly', 'monthly']), default='daily')
    
    response = logic.get_payment_summary(period)
    
    if "error" in response:
        click.secho(response["error"], fg="red")
        return
        
    start_date = response['start_date'].strftime('%d %b %Y')
    end_date = response['end_date'].strftime('%d %b %Y')
    summary = response.get("summary", {})
    
    click.secho(f"\nReport for period: {start_date} to {end_date}", fg="cyan")
    if not summary:
        click.secho("No payments recorded in this period.", fg="yellow")
        return

    headers = ["Payment Method", "Total Amount Collected"]
    table_data = [[method, f"Rs. {amount:.2f}"] for method, amount in summary.items()]
    click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))

