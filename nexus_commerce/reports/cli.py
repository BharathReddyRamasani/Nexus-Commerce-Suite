import click
from tabulate import tabulate
from . import logic

def profit_report_flow():
    """Interactive flow for the profit and revenue report."""
    click.secho("\n--- Profit & Revenue Report ---", fg="blue", bold=True)
    period = click.prompt("Select period (daily, weekly, monthly)", type=click.Choice(['daily', 'weekly', 'monthly']), default='daily')
    
    response = logic.get_profit_report(period)
    
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

def sale_simulator_flow():
    """Interactive flow for simulating the financial impact of a sale."""
    click.secho("\n--- Sale Simulator ---", fg="blue", bold=True)
    
    try:
        discount = click.prompt("Enter discount percentage (e.g., 20 for 20%)", type=float)
        if not (0 < discount < 100):
            click.secho("Error: Please enter a discount between 0 and 100.", fg="red")
            return
    except (ValueError, click.exceptions.Abort):
        click.secho("Invalid input. Please enter a number.", fg="red")
        return
        
    sku_input = click.prompt("Enter product SKUs to include (comma-separated)")
    if not sku_input.strip():
        click.secho("No SKUs entered. Aborting simulation.", fg="yellow")
        return
        
    skus = [sku.strip().upper() for sku in sku_input.split(',')]

    response = logic.simulate_sale(discount, skus)
    results = response.get("data", [])

    if not results:
        click.secho("Could not simulate sale for the given SKUs.", fg="yellow")
        return

    click.secho(f"\n--- Simulation Results for a {discount}% Discount ---", fg="cyan")
    headers = ["Name", "Original Price", "Discounted Price", "Original Profit", "New Profit"]
    table_data = []
    critical_insights = []

    for res in results:
        if "error" in res:
            table_data.append([f"SKU: {res['sku']}", res['error'], "-", "-", "-"])
            continue

        new_profit = res['new_profit']
        new_profit_color = "red" if new_profit < 0 else "green"
        new_profit_text = click.style(f"Rs. {new_profit:.2f}", fg=new_profit_color)
        
        table_data.append([
            res['name'],
            f"Rs. {res['original_price']:.2f}",
            f"Rs. {res['discounted_price']:.2f}",
            f"Rs. {res['original_profit']:.2f}",
            new_profit_text
        ])

        if new_profit < 0:
            critical_insights.append(f"A {discount}% discount on '{res['name']}' ({res['sku']}) will result in a LOSS of Rs. {abs(new_profit):.2f} per unit.")

    click.echo(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

    if critical_insights:
        click.secho("\n⚠️  Critical Insights:", fg="yellow", bold=True)
        for insight in critical_insights:
            click.secho(f"- {insight}", fg="yellow")

