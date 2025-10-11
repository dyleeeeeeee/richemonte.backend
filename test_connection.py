"""
Quick test to verify Supabase connection
"""
from core import get_supabase_client

print("Testing Supabase connection...")
supabase = get_supabase_client()

print(f"Supabase URL: {supabase.supabase_url}")
print(f"Key (first 10 chars): {supabase.supabase_key[:10]}...")

print("\nQuerying users table...")
result = supabase.table('users').select('email, full_name').limit(5).execute()

print(f"Query successful: {len(result.data)} users found")
print("\nUsers in database:")
for user in result.data:
    print(f"  - {user.get('email')} ({user.get('full_name')})")

print("\n✅ Connection works!")
