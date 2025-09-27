from ..common.supabase_client import get_supabase_client

def add_customer(name, phone, email):
    """
    Adds a new customer to the database.
    Returns a string indicating success or failure.
    """
    supabase = get_supabase_client()
    try:
        customer_data = {"name": name, "phone": phone, "email": email}
        
        response = supabase.table("customers").insert(customer_data).execute()
        
        # Robust error checking for Supabase v2
        if hasattr(response, 'error') and response.error:
            raise Exception(response.error.message)
            
        return f"Success: Customer '{name}' added."

    except Exception as e:
        # Provide more specific and user-friendly error messages
        error_str = str(e).lower()
        if 'unique constraint' in error_str and 'phone' in error_str:
            return f"Error: A customer with the phone number '{phone}' already exists."
        elif 'unique constraint' in error_str and 'email' in error_str:
            return f"Error: A customer with the email '{email}' already exists."
        else:
            return f"Error: An unexpected database error occurred. Details: {e}"

def find_customer_by_phone(phone):
    """
    Finds a customer by their phone number and retrieves their complete purchase history.
    This function performs multiple queries to build a comprehensive customer profile.
    Returns a dictionary with customer data or an error string/None.
    """
    supabase = get_supabase_client()
    try:
        # Step 1: Find the customer by their unique phone number.
        response = supabase.table("customers").select("id, name, phone, email").eq("phone", phone).maybe_single().execute()
        
        if not response.data:
            return None # Return None if no customer is found
        
        customer_data = response.data

        # Step 2: Find all sales associated with that customer's ID.
        sales_response = supabase.table("sales").select("*").eq("customer_id", customer_data['id']).execute()
        customer_data['sales'] = sales_response.data
        
        # Step 3: For each sale, find all the individual items that were part of it.
        # This uses a Supabase feature to fetch related product details in the same query.
        for sale in customer_data['sales']:
            items_response = supabase.table("sale_items").select("*, products(*)").eq("sale_id", sale['id']).execute()
            # The key 'items' is used here, which the frontend expects.
            sale['items'] = items_response.data
            
        return customer_data
    except Exception as e:
        return f"Error fetching customer history. Please check the connection and try again. Details: {e}"

def get_all_customers():
    """
    Retrieves a list of all customers from the database, ordered by name.
    Returns a list of customer dictionaries or an error string.
    """
    supabase = get_supabase_client()
    try:
        response = supabase.table("customers").select("*").order("name").execute()
        return response.data
    except Exception as e:
        return f"Error: Could not fetch customers. Details: {e}"

