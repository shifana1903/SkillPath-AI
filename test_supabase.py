import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

result = supabase.table("learners").select("*").limit(1).execute()

print("Supabase connection successful!")
print(result.data)