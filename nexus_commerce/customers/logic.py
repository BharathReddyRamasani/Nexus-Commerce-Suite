"""
Nexus Commerce Suite — Customer Logic
========================================
CRUD operations and purchase history for customers.
"""
import logging
import streamlit as st
from ..common.supabase_client import get_supabase_client

logger = logging.getLogger("nexus_commerce.customers")


def add_customer(name: str, phone: str, email: str) -> str:
    """Add a new customer. Returns success/error message string."""
    supabase = get_supabase_client()
    try:
        customer_data = {
            "name": name.strip(),
            "phone": phone.strip(),
            "email": email.strip() if email else None,
            "user_id": st.session_state.get("user_id")
        }
        logger.info("Adding customer: %s (%s)", name, phone)
        response = supabase.table("customers").insert(customer_data).execute()

        if hasattr(response, 'error') and response.error:
            raise Exception(response.error.message)

        logger.info("Customer '%s' added successfully.", name)
        return f"Success: Customer '{name}' added."

    except Exception as e:
        error_str = str(e).lower()
        if 'unique constraint' in error_str and 'phone' in error_str:
            return f"Error: A customer with phone '{phone}' already exists."
        elif 'unique constraint' in error_str and 'email' in error_str:
            return f"Error: A customer with email '{email}' already exists."
        logger.error("Failed to add customer '%s': %s", name, e)
        return f"Error: An unexpected database error occurred. Details: {e}"


def find_customer_by_phone(phone: str):
    """
    Find a customer and their complete purchase history.
    Returns: dict with customer data + sales, None if not found, or error string.
    """
    supabase = get_supabase_client()
    try:
        logger.info("Looking up customer by phone: %s", phone)
        response = supabase.table("customers").select("id, name, phone, email") \
            .eq("phone", phone.strip()) \
            .eq("user_id", st.session_state.get("user_id")) \
            .maybe_single().execute()

        if not response.data:
            return None

        customer_data = response.data

        # Fetch sales
        sales_response = supabase.table("sales").select("*") \
            .eq("customer_id", customer_data['id']) \
            .eq("user_id", st.session_state.get("user_id")) \
            .execute()
        customer_data['sales'] = sales_response.data

        # Fetch items for each sale (with product details)
        for sale in customer_data['sales']:
            items_response = supabase.table("sale_items").select("*, products(*)").eq("sale_id", sale['id']).execute()
            sale['items'] = items_response.data

        logger.info("Found customer '%s' with %d sales.", customer_data['name'], len(customer_data['sales']))
        return customer_data
    except Exception as e:
        logger.error("Customer lookup failed for phone '%s': %s", phone, e)
        return f"Error fetching customer history. Details: {e}"


def get_all_customers() -> list | str:
    """Retrieve all customers ordered by name. Returns list or error string."""
    supabase = get_supabase_client()
    try:
        response = supabase.table("customers").select("*") \
            .eq("user_id", st.session_state.get("user_id")) \
            .order("name").execute()
        return response.data
    except Exception as e:
        logger.error("Failed to fetch customers: %s", e)
        return f"Error: Could not fetch customers. Details: {e}"


def update_customer(phone: str, updates: dict) -> str:
    """Update customer details by phone number. Returns success/error message."""
    supabase = get_supabase_client()
    try:
        phone_clean = phone.strip()
        logger.info("Updating customer phone '%s' with: %s", phone_clean, updates)
        response = supabase.table("customers").update(updates) \
            .eq("phone", phone_clean) \
            .eq("user_id", st.session_state.get("user_id")) \
            .execute()
        if hasattr(response, 'error') and response.error:
            raise Exception(response.error.message)
        if not response.data:
            return f"Error: Customer with phone '{phone_clean}' not found."
        logger.info("Customer phone '%s' updated.", phone_clean)
        return f"Success: Customer with phone '{phone_clean}' has been updated."
    except Exception as e:
        if 'unique constraint' in str(e).lower():
            return f"Error: That phone number or email is already in use by another customer."
        logger.error("Failed to update customer '%s': %s", phone, e)
        return f"Error: Could not update customer. Details: {e}"


def delete_customer_by_phone(phone: str) -> str:
    """Delete a customer by phone number. Returns success/error message."""
    supabase = get_supabase_client()
    try:
        phone_clean = phone.strip()
        logger.info("Deleting customer phone: %s", phone_clean)

        # Check existence
        customer_res = supabase.table("customers").select("id, name") \
            .eq("phone", phone_clean) \
            .eq("user_id", st.session_state.get("user_id")) \
            .maybe_single().execute()
        if not customer_res.data:
            return f"Error: Customer with phone '{phone_clean}' not found."

        customer_name = customer_res.data['name']

        response = supabase.table("customers").delete() \
            .eq("phone", phone_clean) \
            .eq("user_id", st.session_state.get("user_id")) \
            .execute()
        if hasattr(response, 'error') and response.error:
            raise Exception(response.error.message)

        logger.info("Customer '%s' (phone: %s) deleted.", customer_name, phone_clean)
        return f"Success: Customer '{customer_name}' ({phone_clean}) has been deleted."
    except Exception as e:
        logger.error("Failed to delete customer '%s': %s", phone, e)
        return f"Error: Could not delete customer. Details: {e}"
