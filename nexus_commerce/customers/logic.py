from ..common.supabase_client import get_supabase_client

def add_customer(name, phone, email):
    """Adds a new customer to the database."""
    supabase = get_supabase_client()
    try:
        customer_data = {"name": name, "phone": phone, "email": email}
        
        response = supabase.table("customers").insert(customer_data).execute()
        
        if hasattr(response, 'error') and response.error:
            raise Exception(response.error.message)
            
        return f"Success: Customer '{name}' added."

    except Exception as e:
        print("\n--- RAW DATABASE ERROR ---")
        print(repr(e))
        print("--------------------------\n")
        if 'unique constraint' in str(e).lower() and 'phone' in str(e).lower():
            return f"Error: A customer with phone '{phone}' already exists."
        elif 'unique constraint' in str(e).lower() and 'email' in str(e).lower():
            return f"Error: A customer with email '{email}' already exists."
        else:
            return f"Error: An unexpected database error occurred. Please check the console for details."


def find_customer_by_phone(phone):
    """Finds a customer by their phone number and retrieves their complete history."""
    supabase = get_supabase_client()
    try:
        response = supabase.table("customers").select("id, name, phone, email").eq("phone", phone).execute()
        if not response.data:
            return None
        customer_data = response.data[0]

        sales_response = supabase.table("sales").select("*").eq("customer_id", customer_data['id']).execute()
        customer_data['sales'] = sales_response.data
        
        for sale in customer_data['sales']:
            items_response = supabase.table("sale_items").select("*, products(*)").eq("sale_id", sale['id']).execute()
            sale['items'] = items_response.data
            
        return customer_data
    except Exception as e:
        return f"Error fetching customer history. Details: {e}"


def get_all_customers():
    """Retrieves all customers from the database."""
    supabase = get_supabase_client()
    try:
        response = supabase.table("customers").select("*").order("name").execute()
        return response.data
    except Exception as e:
        return f"Error: Could not fetch customers. Details: {e}"

