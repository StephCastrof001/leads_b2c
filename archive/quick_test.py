from instagrapi import Client
import time
import json

print("="*60)
print("🚀 QUICK TEST - clinicavesaliooficial")
print("="*60)

# SessionID (Manual de https://www.instagram.com/developer/cookies/)
sessionid = "COPIA_AQUI_DE_LA_COOKIE_sessionid"

client = Client()
client.sessionid = sessionid
client.mid = "mid_"
print(f"✅ Session: {client.sessionid[:30]}...")
time.sleep(2)

print(f"\n📍 Target: 'clinicavesaliooficial'...")

try:
    # Test 1: User Info
    user = client.user_info_by_username("clinicavesaliooficial")
    print(f"✅ User: {user.username}, ID: {user.pk}")
    print(f"✅ Followers: {user.followers_count:,}")
    
    # Test 2: Followers
    followers = client.user_followers(user.pk, limit=10)
    print(f"\n✅ Followers: {len(followers)}")
    
    # Samples
    print(f"\n   Samples:")
    for i, f in enumerate(followers[:5], 1):
        print(f"      {i}. @{f.username} (ID: {f.pk})")
    
    # Save
    with open("followers_sample.json", "w") as f:
        json.dump({"target": "clinicavesaliooficial", "count": len(followers), "samples": [{"username": fl.username} for fl in followers[:5]]}, f, indent=2)
    
    print(f"\n✅ Saved: followers_sample.json")
    
except Exception as e:
    print(f"⚠️ Error: {type(e).__name__}: {e}")

finally:
    client.close()
    print("\n✅ Done!")
