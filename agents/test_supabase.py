
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL", "").strip()
key = os.getenv("SUPABASE_PUBLISHABLE_KEY", "").strip()

print("URL loaded:", bool(url))
print("Key loaded:", bool(key))
print("Key format correct:", key.startswith("sb_publishable_"))

supabase = create_client(url, key)

result = supabase.table("learners").select("*").limit(1).execute()

print("Supabase connection successful!")
print("Data:", result.data)
