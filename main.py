import os
import click
from nexus_commerce.inventory.cli import (
    add_product_flow,
    list_products_flow,
    find_product_flow,
    update_product_flow,
    adjust_stock_flow
)
from nexus_commerce.customers.cli import (
    add_customer_flow,
    list_customers_flow,
    find_customer_history_flow
)
from nexus_commerce.sales.cli import record_sale_flow
from nexus_commerce.reports.cli import (
    profit_report_flow,
    product_health_report_flow,
    payment_summary_flow,
    sale_simulator_flow  #
)

def clear_screen():
    """Clears the terminal screen for a cleaner user interface."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Prints a consistent, styled header for all menus."""
    click.secho("\n" + "="*50, fg="cyan")
    click.secho(f"      {title.upper()}", fg="cyan", bold=True)
    click.secho("="*50 + "\n", fg="cyan")

def product_menu():
    """Displays and handles the menu for all Inventory Management tasks."""
    while True:
        clear_screen()
        print_header("Inventory Management")
        click.echo("1. Add New Product")
        click.echo("2. List All Products")
        click.echo("3. Find Product by SKU")
        click.echo("4. Update Product Details (Name/Price)")
        click.echo("5. Adjust Stock Quantity (Manual Correction)")
        click.echo("0. Back to Main Menu")
        choice = click.prompt("Select an option", type=str)

        if choice == '1':
            add_product_flow()
        elif choice == '2':
            list_products_flow()
        elif choice == '3':
            find_product_flow()
        elif choice == '4':
            update_product_flow()
        elif choice == '5':
            adjust_stock_flow()
        elif choice == '0':
            break
        else:
            click.secho("Invalid option, please try again.", fg="red")

        click.pause("\nPress any key to continue...")

def sales_menu():
    """Handles the user flow for recording a new sale."""
    clear_screen()
    print_header("Sales Terminal")
    record_sale_flow()
    click.pause("\nPress any key to continue...")

def customer_menu():
    """Displays and handles the menu for Customer Management (CRM)."""
    while True:
        clear_screen()
        print_header("Customer Management (CRM)")
        click.echo("1. Add New Customer")
        click.echo("2. List All Customers")
        click.echo("3. View Customer Purchase History")
        click.echo("0. Back to Main Menu")
        choice = click.prompt("Select an option", type=str)

        if choice == '1':
            add_customer_flow()
        elif choice == '2':
            list_customers_flow()
        elif choice == '3':
            find_customer_history_flow()
        elif choice == '0':
            break
        else:
            click.secho("Invalid option, please try again.", fg="red")

        click.pause("\nPress any key to continue...")

def reports_menu():
    """Displays and handles the menu for Business Intelligence Reports."""
    while True:
        clear_screen()
        print_header("Business Intelligence Reports")
        click.echo("1. Profit & Revenue Report")
        click.echo("2. Product Health Status Report")
        click.echo("3. Payment Methods Summary")
        click.echo("4. Simulate a Sale (Strategic Tool)")
        click.echo("0. Back to Main Menu")
        choice = click.prompt("Select an option", type=str)

        if choice == '1':
            profit_report_flow()
        elif choice == '2':
            product_health_report_flow()
        elif choice == '3':
            payment_summary_flow()
        elif choice == '4':
            sale_simulator_flow()
        elif choice == '0':
            break
        else:
            click.secho("Invalid option, please try again.", fg="red")

        click.pause("\nPress any key to continue...")

def main_menu():
    """The main interactive menu loop for the entire application."""
    while True:
        clear_screen()
        print_header("Nexus Commerce Suite - Main Menu")
        click.echo("1. Manage Inventory")
        click.echo("2. Record a New Sale")
        click.echo("3. Manage Customers")
        click.echo("4. View Reports")
        click.echo("0. Exit")
        choice = click.prompt("Select an option", type=str)

        if choice == '1':
            product_menu()
        elif choice == '2':
            sales_menu()
        elif choice == '3':
            customer_menu()
        elif choice == '4':
            reports_menu()
        elif choice == '0':
            click.secho("\nThank you for using Nexus Commerce Suite. Goodbye!", fg="yellow")
            break
        else:
            click.secho("Invalid option, please try again.", fg="red")
            click.pause()

if __name__ == "__main__":
    try:
        from nexus_commerce.common.supabase_client import initialize_supabase_client
        try:
            initialize_supabase_client()
        except (ValueError, ConnectionError) as e:
            click.secho("FATAL ERROR: Could not initialize Supabase connection.", fg="red", bold=True)
            click.secho(str(e), fg="red")
            exit(1) 

        main_menu()
    except (KeyboardInterrupt, EOFError):
        click.secho("\nApplication terminated by user. Goodbye!", fg="yellow")

