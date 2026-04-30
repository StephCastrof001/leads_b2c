"""
SMOKETEST INSTAGRAM FOLLOWERS - SMARTPROXY FREE
"""
from instagrapi import Client
import time

# ============== PROXY FREE TIER (RESIDENCIAL)
PROXY = "http://smartproxy_user:password@77.77.77.77:8080"
TARGET = "nike"
LIMIT = 10

# ============== SETUP
client = Client()
client.set_proxy(PROXY)
print(f"✅ Proxy: {PROXY[:40]}...")

client.pre_login_flow()
print("✅ Pre-flow...")

client.login("ValesNissanCombustible", "20063288")
print("✅ Login..." )

time.sleep(2)

# ============== TEST
print(f"\n📊 Testing: @{TARGET}")

try:
    user = client.user_info_by_username(TARGET)
    print(f"✅ User: {user.pk} - {user.followers_count:,} followers")
    
    followers = client.user_followers(user.pk, limit=LIMIT)
    print(f"\n✅ SUCCESS! {len(followers)} followers")
    
    for i, f in enumerate(followers[:5], 1):
        print(f"   {i}. @{f.username} (ID: {f.pk})")
    
    import json
    result = {
        "target": TARGET,
        "followers_count": user.followers_count,
        "sample_followers": [{"username": f.username, "pk": f.pk} for f in followers[:3]]
    }
    
    with open("/home/ubuntu/docs_dev/smoketest_result.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n{'='*40}")
    print(f"✅ TEST COMPLETADO!")
    print(f"Archivo: smoketest_result.json")
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
finally:
    client.close()
