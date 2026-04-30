"""
🚀 FINAL SCRIPT - clinicavesaliooficial + Followers
"""

from instagrapi import Client
import time
import json

print("="*60)
print("🚀 SMOKE TEST FINAL - clinicavesaliooficial + Followers")
print("="*60)

client = Client()

# Step 1: Pre-flow
print("\nStep 1: Pre-flow...")
client.pre_login_flow()
print("✅ OK")
time.sleep(2)

# Step 2: Session
print("\nStep 2: Session...")
sessionid = "COPIA_SESSIONID_AQUI"

sessionid = input("\n   Pega el sessionid: ").strip() if sessionid == "COPIA_SESSIONID_AQUI" else sessionid
print(f"✅ Session: {sessionid[:30]}...")
time.sleep(2)

# Step 3: User Info
print(f"\nStep 3: User Info: 'clinicavesaliooficial'...")
for retry in range(3):
    try:
        user = client.user_info_by_username("clinicavesaliooficial")
        print(f"✅ SUCCESS! ID: {user.pk}")
        break
    except Exception as e:
        print(f"⚠️ Retry {retry+1}: {type(e).__name__}")
        time.sleep(3)
else:
    print("❌ All retries failed")

# Step 4: Followers
print(f"\nStep 4: Followers...")
try:
    followers = client.user_followers(user.pk)
    followers = list(followers)  # Convert generator
    followers = followers[:10]
    print(f"✅ SUCCESS! Total: {len(followers)}")
    
    print(f"\n   Samples:")
    for i, f in enumerate(followers[:5], 1):
        print(f"      {i}. @{f.username} (ID: {f.pk})")
    
    # Step 5: Save
    print(f"\nStep 5: Saving...")
    with open("followers_sample.json", "w") as f:
        json.dump({"target": "clinicavesaliooficial", "count": len(followers), "samples": [{"username": fl.username} for fl in followers[:5]]}, f, indent=2)
    print("✅ Saved: followers_sample.json")
    
except Exception as e:
    print(f"⚠️ Error: {type(e).__name__}: {e}")

print(f"\n✅ Done!")
client.close()
