import os
from dotenv import load_dotenv
from supabase import create_client, Client
load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase_client: Client = None

def initialize_supabase_client():
    """Initializes the global Supabase client. To be called once on startup."""
    global supabase_client
    if url and key:
        try:
            supabase_client = create_client(url, key)
        except Exception as e:
            raise ConnectionError(f"Could not create Supabase client. Details: {e}")
    else:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY not found in .env file.")

def get_supabase_client():
    """Returns the shared Supabase client instance. All logic files will call this."""
    if supabase_client is None:
        raise ConnectionError("Supabase client is not initialized. Run initialize_supabase_client() first.")
    return supabase_client


