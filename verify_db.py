
import os
from dotenv import load_dotenv
from supabase import create_client

def verify():
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    print(f"Checking Project: {url}")
    supabase = create_client(url, key)
    
    try:
        # Check Products
        p_res = supabase.table("products").select("id", count="exact").execute()
        print(f"Products Count: {len(p_res.data)}")
        
        # Check Customers
        c_res = supabase.table("customers").select("id", count="exact").execute()
        print(f"Customers Count: {len(c_res.data)}")
        
        # Check Sales
        s_res = supabase.table("sales").select("id", count="exact").execute()
        print(f"Sales Count: {len(s_res.data)}")
        
    except Exception as e:
        print(f"Verification Failed: {e}")

if __name__ == "__main__":
    verify()
