import os
from supabase import create_client, Client

# Initialize the Supabase client
SUPABASE_URL = "https://xzelogoeyuszberazhjp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh6ZWxvZ29leXVzemJlcmF6aGpwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjYzODE2ODMsImV4cCI6MjA0MTk1NzY4M30.RXPCLpdbQ7w6F_z2ORU8m1jYni5oneSiVkNBpJqodB0"  # Dein Supabase anon key
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
