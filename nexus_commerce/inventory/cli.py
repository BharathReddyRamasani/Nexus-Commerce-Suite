import click
from tabulate import tabulate
from . import logic

def add_product_flow():
    """Interactive flow for adding a new product."""
    click.secho("\n--- Add a New Product ---", fg="blue", bold=True)
    name = click.prompt("Enter product name")
    sku = click.prompt("Enter product SKU (unique code)")
    cost_price = click.prompt("Enter cost price", type=float)
    selling_price = click.prompt("Enter selling price", type=float)
    quantity = click.prompt("Enter initial quantity", type=int, default=0)
    
    result = logic.add_product(name, sku, cost_price, selling_price, quantity)
    
    if "Success" in result:
        click.secho(result, fg="green")
    else:
        click.secho(result, fg="red")

def list_products_flow():
    """Flow for listing all products."""
    click.secho("\n--- All Products ---", fg="blue", bold=True)
    products = logic.get_all_products()
    if isinstance(products, list):
        if not products:
            click.secho("No products found in the inventory.", fg="yellow")
            return
        
        headers = ["SKU", "Name", "Qty", "Cost Price", "Selling Price"]
        table_data = [
            [
                p["sku"],
                p["name"],
                p["quantity_on_hand"],
                f"Rs. {p['cost_price']:.2f}",
                f"Rs. {p['selling_price']:.2f}",
            ]
            for p in products
        ]
        click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))
    else:
        click.secho(products, fg="red")

def find_product_flow():
    """Flow for finding a single product by SKU."""
    click.secho("\n--- Find a Product by SKU ---", fg="blue", bold=True)
    sku = click.prompt("Enter the SKU of the product to find")
    product = logic.find_product_by_sku(sku)
    if isinstance(product, dict):
        headers = ["Attribute", "Value"]
        table_data = [
            ["Name", product["name"]],
            ["SKU", product["sku"]],
            ["Quantity on Hand", product["quantity_on_hand"]],
            ["Cost Price", f"Rs. {product['cost_price']:.2f}"],
            ["Selling Price", f"Rs. {product['selling_price']:.2f}"],
        ]
        click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))
    elif product is None:
        click.secho(f"No product found with SKU '{sku.upper()}'.", fg="yellow")
    else:
        click.secho(product, fg="red")

def update_product_flow():
    """Interactive flow for updating an existing product's details (name/price)."""
    click.secho("\n--- Update Product Details (Name/Price) ---", fg="blue", bold=True)
    sku_to_update = click.prompt("Enter the SKU of the product to update")
    
    product = logic.find_product_by_sku(sku_to_update)
    
    if not isinstance(product, dict):
        if product is None:
            click.secho(f"Error: No product found with SKU '{sku_to_update.upper()}'.", fg="red")
        else:
            click.secho(product, fg="red") 
        return

    click.echo("\nProduct found. Enter new details below (press Enter to keep current value).")
    
    updates = {}
    
    new_name = click.prompt(f"Enter new name", default=product['name'], show_default=True)
    if new_name != product['name']:
        updates['name'] = new_name

    new_selling_price = click.prompt(f"Enter new selling price", default=product['selling_price'], type=float, show_default=True)
    if new_selling_price != product['selling_price']:
        updates['selling_price'] = new_selling_price

    new_cost_price = click.prompt(f"Enter new cost price", default=product['cost_price'], type=float, show_default=True)
    if new_cost_price != product['cost_price']:
        updates['cost_price'] = new_cost_price

    if not updates:
        click.secho("No changes were made.", fg="yellow")
        return

    result = logic.update_product_by_sku(sku_to_update, updates)
    if "Success" in result:
        click.secho(result, fg="green")
    else:
        click.secho(result, fg="red")

def adjust_stock_flow():
    """Interactive flow for manually adjusting stock quantity for auditing."""
    click.secho("\n--- Adjust Stock Quantity ---", fg="blue", bold=True)
    sku = click.prompt("Enter the SKU of the product to adjust")
    
    try:
        change = click.prompt("Enter the change in quantity (e.g., -1 for removal, 5 for addition)", type=int)
    except (ValueError, click.exceptions.Abort):
        click.secho("Invalid number. Please enter an integer.", fg="red")
        return
        
    reason = click.prompt("Enter the reason for this adjustment (e.g., 'Damaged item', 'Stock count correction')")
    if not reason.strip():
        click.secho("A reason is required for all stock adjustments.", fg="red")
        return
        
    result = logic.adjust_stock_quantity(sku, change, reason)
    if "Success" in result:
        click.secho(result, fg="green")
    else:
        click.secho(result, fg="red")

