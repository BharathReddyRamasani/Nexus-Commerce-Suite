import os
from dotenv import load_dotenv
from supabase import create_client

# Load .env from the root directory
load_dotenv('d:/tekworks/Nexus-Commerce-Suite/.env')

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_KEY not found in .env")
    exit(1)

supabase = create_client(url, key)

print(f"Connecting to: {url}")

try:
    # Try to fetch one row from stock_adjustments to see columns
    print("Checking stock_adjustments table...")
    res = supabase.table("stock_adjustments").select("*").limit(1).execute()
    if res.data:
        print("Columns in stock_adjustments:", res.data[0].keys())
    else:
        print("stock_adjustments table is empty.")
    
    # Try to check if warehouses table exists
    print("\nChecking warehouses table...")
    try:
        res_w = supabase.table("warehouses").select("*").limit(1).execute()
        print("Warehouses table exists. Data:", res_w.data)
    except Exception as e:
        print("Warehouses table does not exist or error:", e)

except Exception as e:
    print("\nError checking schema:", e)
