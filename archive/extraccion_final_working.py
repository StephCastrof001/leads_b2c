"""
FINAL EXTRACTION - clinicavesaliooficial + followers
"""

from instagrapi import Client
import time
import json

print("="*60)
print("🚀 FINAL EXTRACTION - clinicavesaliooficial + Followers")
print("="*60)

client = Client()

# Step 1: Pre-flow
print("\nStep 1: Pre-flow...")
client.pre_login_flow()
print("✅ OK")
time.sleep(2)

# Step 2: Web Flow
print("\nStep 2: Web Flow (Manual Session)...")
print("""
   1. Abre: https://www.instagram.com/accounts/login/
   2. Ingresa tus credentials
   3. Pestaña F12 -> Network -> Headers -> Cookies
   4. Copia el valor de "sessionid"
""")

# Read sessionid from input
try:
    sessionid = input("\n   5. Pega el sessionid: ").strip()
except EOFError:
    sessionid = "COPIA_SESSIONID_AQUI"

print(f"   ✅ Session: {sessionid[:30]}...")

# Test 1: User Info
print(f"\nStep 3: User Info: 'clinicavesaliooficial'...")
try:
    user = client.user_info_by_username("clinicavesaliooficial")
    print(f"✅ User: {user.username}, ID: {user.pk}")
    print(f"✅ Followers: {user.followers_count:,}")
    
    # Test 2: Followers
    print(f"\nStep 4: Followers (limit=10)...")
    followers = client.user_followers(user.pk, limit=10)
    print(f"✅ Total: {len(followers)}")
    
    # Samples
    print(f"\n   Samples ({min(5, len(followers))}...")
    for i, f in enumerate(followers[:min(5, len(followers))], 1):
        print(f"      {i}. @{f.username} (ID: {f.pk})")
    
    # Save to File
    print(f"\nStep 5: Saving files...")
    with open("followers_sample.json", "w") as f:
        json.dump({
            "target": "clinicavesaliooficial",
            "count": len(followers),
            "samples": [{"username": fl.username, "pk": fl.pk} for fl in followers[:5]]
        }, f, indent=2)
    
    with open("followers_sample.csv", "w") as f:
        f.write("index,username,pk\n")
        for i, ff in enumerate(followers[:10], 1):
            f.write(f"{i},{ff.username},{ff.pk}\n")
    
    print("✅ Saved: followers_sample.json")
    print("✅ Saved: followers_sample.csv")
    
except Exception as e:
    print(f"⚠️ Error: {type(e).__name__}")
    print(f"   Message: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*60}")
print("✅ Done!")
print(f"{'='*60}")
