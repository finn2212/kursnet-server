import os
from supabase import create_client, Client

# Initialize the Supabase client
SUPABASE_URL = "https://lnacwzshltbjotnpvien.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxuYWN3enNobHRiam90bnB2aWVuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcxOTExOTM1MCwiZXhwIjoyMDM0Njk1MzUwfQ.ZSmKel80I_o3JbBKbK0plyzxQ-6xOBzx7A4edFjcnLU"  # Dein Supabase anon key
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
