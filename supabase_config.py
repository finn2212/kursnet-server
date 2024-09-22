from supabase import create_client, Client

# Supabase-Verbindungsdetails
url: str = "https://xzelogoeyuszberazhjp.supabase.co"  # Deine Supabase URL
anon_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh6ZWxvZ29leXVzemJlcmF6aGpwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjYzODE2ODMsImV4cCI6MjA0MTk1NzY4M30.RXPCLpdbQ7w6F_z2ORU8m1jYni5oneSiVkNBpJqodB0"  # Dein Supabase anon key

# Supabase Client erstellen
supabase: Client = create_client(url, anon_key)
