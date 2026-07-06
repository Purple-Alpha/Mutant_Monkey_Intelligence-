"""
HANDSHAKE TEST - Step 1 of Immediate Directives
Run this from MMI:
    python tests/test_handshake.py
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("\n=== SOCIAL ARCHITECT — SUPABASE HANDSHAKE TEST ===\n")

# Step 1: Check env vars are loaded
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not url:
    print("FAIL — SUPABASE_URL not found in .env")
    sys.exit(1)
if not key:
    print("FAIL — SUPABASE_SERVICE_ROLE_KEY not found in .env")
    sys.exit(1)

print(f"ENV CHECK     OK — URL: {url[:30]}...")
print(f"ENV CHECK     OK — Service key loaded ({len(key)} chars)\n")

# Step 2: Try importing supabase
try:
    from supabase import create_client, Client
    print("IMPORT        OK — supabase-py found")
except ImportError:
    print("FAIL — supabase not installed. Run: pip install supabase")
    sys.exit(1)

# Step 3: Try creating client
try:
    supabase: Client = create_client(url, key)
    print("CLIENT        OK — Supabase client created")
except Exception as e:
    print(f"FAIL — Could not create client: {e}")
    sys.exit(1)

# Step 4: Ping Supabase with a real query
try:
    response = supabase.table("profiles").select("id").limit(1).execute()
    print(f"PING          OK — profiles table responded")
    print(f"              Row count returned: {len(response.data)}")
except Exception as e:
    print(f"PING FAIL — Could not query profiles table: {e}")
    print("              (Table may not exist yet — check Supabase dashboard)")

# Step 5: Check briefing_summary table exists (needed for MAVEN directive)
try:
    response = supabase.table("briefing_summary").select("id").limit(1).execute()
    print(f"TABLE CHECK   OK — briefing_summary exists")
except Exception as e:
    print(f"TABLE CHECK   MISSING — briefing_summary not found: {e}")
    print("              -> This table needs to be created (Step 3 of directives)")

print("\n=== HANDSHAKE COMPLETE ===\n")
