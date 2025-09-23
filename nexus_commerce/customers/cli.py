import click
from tabulate import tabulate
from . import logic

def add_customer_flow():
    """Interactive flow for adding a new customer."""
    click.secho("\n--- Add a New Customer ---", fg="blue", bold=True)
    name = click.prompt("Enter customer name")
    phone = click.prompt("Enter customer phone number")
    email = click.prompt("Enter customer email (optional, press Enter to skip)", default="", show_default=False)
    
    result = logic.add_customer(name, phone, email)
    if "Success" in result:
        click.secho(result, fg="green")
    else:
        click.secho(result, fg="red")

def list_customers_flow():
    """Flow for listing all customers."""
    click.secho("\n--- All Customers ---", fg="blue", bold=True)
    customers = logic.get_all_customers()
    if isinstance(customers, list):
        if not customers:
            click.secho("No customers found.", fg="yellow")
            return
        
        headers = ["Name", "Phone", "Email"]
        table_data = [[c['name'], c['phone'], c.get('email', 'N/A')] for c in customers]
        click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))
    else:
        click.secho(customers, fg="red") 

def find_customer_history_flow():
    """Flow for finding a customer and displaying their purchase history."""
    click.secho("\n--- Customer Purchase History ---", fg="blue", bold=True)
    phone = click.prompt("Enter the phone number of the customer to find")
    customer = logic.find_customer_by_phone(phone)
    
    if isinstance(customer, str): 
        click.secho(customer, fg="red")
        return
    if customer is None:
        click.secho(f"No customer found with phone number '{phone}'.", fg="yellow")
        return

    click.secho(f"\nPurchase History for: {customer['name']} ({customer['phone']})", fg="cyan", bold=True)
    
    if not customer.get('sales'):
        click.secho("This customer has no purchase history.", fg="yellow")
        return

    for sale in customer['sales']:
        sale_date = sale['sale_date']
        total = sale['total_amount']
        click.echo("\n" + "-"*50)
        click.echo(f"Sale Date: {sale_date} | Total: Rs. {total:.2f}")
        click.echo("-" * 50)
        
        headers = ["Product Name", "SKU", "Quantity", "Price"]
        table_data = []
 
        for item in sale['items']:
            product_name = item.get('products', {}).get('name', 'N/A')
            product_sku = item.get('products', {}).get('sku', 'N/A')
            table_data.append([
                product_name,
                product_sku,
                item['quantity'],
                f"Rs. {item['price_per_unit']:.2f}"
            ])
        click.echo(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))


