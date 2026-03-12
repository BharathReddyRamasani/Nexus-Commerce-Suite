import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('d:/tekworks/Nexus-Commerce-Suite/.env')

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

try:
    # Query information_schema to see columns of stock_adjustments
    # Use rpc if possible or a raw query if client supports it
    # Since supabase-py is high-level, let's try a trick: insert a dummy row that fails and catch the full error
    # Or just try to select everything and see if we get an empty list with keys
    
    print("Checking columns of stock_adjustments via rpc or select...")
    
    # Try a raw SQL query via postgrest if possible (usually not directly)
    # Let's try to find if any records exist at all
    res = supabase.table("stock_adjustments").select("*").limit(1).execute()
    if res.data:
        print("Existing row data keys:", res.data[0].keys())
    else:
        print("Table is empty, trying to insert an empty object to see column error...")
        try:
            supabase.table("stock_adjustments").insert({}).execute()
        except Exception as e:
            print("Insert error (revealing columns?):", e)

except Exception as e:
    print("Error:", e)
