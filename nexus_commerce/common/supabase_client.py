import os
from dotenv import load_dotenv
from supabase import create_client, Client

# --- Global variable to hold the single, shared client instance ---
# We use a leading underscore to indicate it's for internal use within this module.
_supabase_client: Client = None

def get_supabase_client():
    """
    Creates and returns the Supabase client instance.
    Uses a singleton pattern to ensure only one client is created per session.
    This is the only function that other modules should import.
    """
    global _supabase_client

    # If the client has not been created yet, this block will run.
    if _supabase_client is None:
        # Load environment variables from the .env file or Streamlit secrets
        load_dotenv()
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")

        # A robust check for credentials
        if not url or not key:
            raise ValueError("FATAL ERROR: SUPABASE_URL and SUPABASE_KEY must be set in your .env file or Streamlit secrets.")

        try:
            # Create the client and store it in the global variable for reuse.
            _supabase_client = create_client(url, key)
        except Exception as e:
            raise ConnectionError(f"Could not create Supabase client. Please check your credentials. Details: {e}")
    
    # Return the existing client instance.
    return _supabase_client

def check_connection():
    """
    A simple function to be called on startup to explicitly verify credentials
    and provide a clear error message to the user if they are invalid.
    """
    try:
        # Attempt to get the client, which will trigger initialization if needed.
        get_supabase_client()
        return True
    except (ValueError, ConnectionError) as e:
        # If an error occurs, re-raise it to be caught by the main app page.
        raise e

