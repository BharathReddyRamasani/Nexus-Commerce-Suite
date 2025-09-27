import os
from dotenv import load_dotenv
from supabase import create_client, Client

# --- Global variable to hold the single client instance ---
# This is a best practice to ensure we don't create multiple connections.
supabase_client: Client = None

def initialize_supabase_client():
    """
    Initializes the global Supabase client.
    This function should be called only once when the application starts.
    It reads credentials from the .env file and establishes the connection.
    """
    global supabase_client

    # Load environment variables from the .env file in the project root
    load_dotenv()

    # Get the Supabase URL and Key from the environment
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")

    # Robust check to ensure credentials are provided
    if not url or not key:
        raise ValueError("FATAL ERROR: SUPABASE_URL and SUPABASE_KEY must be set in your .env file.")

    try:
        # Create the client instance and store it in the global variable
        supabase_client = create_client(url, key)
    except Exception as e:
        # Catch any other potential errors during client creation
        raise ConnectionError(f"Could not create Supabase client. Please check your credentials. Details: {e}")

def get_supabase_client():
    """
    Returns the shared Supabase client instance.
    All logic files across the application will call this function to get the
    initialized client and interact with the database.
    """
    if supabase_client is None:
        # This is a safeguard. If any part of the code tries to get the client
        # before it's been initialized, it will raise a clear error.
        raise ConnectionError("Supabase client has not been initialized. Please run initialize_supabase_client() on startup.")
    
    return supabase_client

