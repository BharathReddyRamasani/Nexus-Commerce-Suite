import click
from . import logic

def record_sale_flow():
    """Interactive flow for recording a new sale transaction."""
    click.secho("\n--- Record a New Sale ---", fg="blue", bold=True)
    
    sale_items_info = []
    while True:
        sku = click.prompt("Enter product SKU (or 'done' to finish)", type=str)
        if sku.lower() == 'done':
            if not sale_items_info:
                click.secho("No items added. Aborting sale.", fg="yellow")
                return
            break
        
        try:
            quantity = click.prompt(f"Enter quantity for {sku.upper()}", type=int)
            if quantity <= 0:
                raise ValueError()
            sale_items_info.append({"sku": sku, "quantity": quantity})
        except (ValueError, click.exceptions.Abort):
            click.secho("Invalid quantity. Please enter a positive number.", fg="red")
    
    payments_info = []
    while True:
        method = click.prompt("Enter payment method (e.g., Cash, UPI, Card) (or 'done' to finish)", type=str)
        if method.lower() == 'done':
            if not payments_info:
                click.secho("No payment method provided. Aborting sale.", fg="yellow")
                return
            break
        
        try:
            amount = click.prompt(f"Enter amount for {method}", type=float)
            if amount <= 0:
                raise ValueError()
            payments_info.append({"method": method, "amount": amount})
        except (ValueError, click.exceptions.Abort):
            click.secho("Invalid amount. Please enter a positive number.", fg="red")
            
    customer_phone = click.prompt("Enter customer phone (optional, press Enter to skip)", default="", show_default=False)
    if not customer_phone.strip():
        customer_phone = None

    response = logic.record_sale(sale_items_info, payments_info, customer_phone)
    
    if response['success']:
        click.secho(response['message'], fg="green", bold=True)
        if response['alerts']:
            click.secho("\n--- CRITICAL ALERTS ---", fg="yellow", bold=True)
            for alert in response['alerts']:
                click.secho(alert, fg="yellow")
    else:
        click.secho(response['message'], fg="red")

