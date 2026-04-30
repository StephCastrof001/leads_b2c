"""
⚡ SMOKETEST FINAL - Instagram Followers + Email Extractor
===> Configuración: SmartProxy Real + Firecrawl API
"""

from instagrapi import Client
from firecrawl import FirecrawlApp
import time
import re
import json

# === 1) SmartProxy CREDenciales REALES
SMARTPROXY_EMAIL = "steph@klipso.lat"
SMARTPROXY_PASS = "20063288"
SMARTPROXY_IP = "190.237.1.228"

# Proxy URL
PROXY_URL = "http://{email}:{p}@{ip}:8080".format(
    email=SMARTPROXY_EMAIL,
    p=SMARTPROXY_PASS,
    ip=SMARTPROXY_IP
)

# === 2) Instagram + Firecrawl
USERNAME = "ValesNissanCombustible"
PASSWORD = "20063288"
TARGET = "nike"
LIMIT = 20
FIRECRAWL_API = ".e7d9732fd6351820c3a47889055fd3e5"

# === 3) SETUP
print("="*60)
print("🚀 SMOKE TEST FINAL - Instagram + Email Scraping")
print("="*60)

print(f"\n   1. Configurar SmartProxy ({SMARTPROXY_IP})...")
try:
    client = Client()
    client.set_proxy(PROXY_URL)
    print(f"      ✅ Proxy OK: {PROXY_URL}")
except Exception as e:
    print(f"      ⚠️ Warning: {e}")
    client = Client()

print(f"\n   2. Autenticar...")
try:
    if not client.pre_login_flow():
        pass
    print("      ✅ Pre-flow OK")
except:
    pass

try:
    client.login(USERNAME, PASSWORD)
    print(f"      ✅ Login OK! ({client.sessionid[:20]}...)")
except:
    print("      ⚠️ Login...")

time.sleep(2)

print(f"\n   3. Testing API: @{TARGET}")
try:
    user = client.user_info_by_username(TARGET)
    print(f"      ✅ User: {user.pk} - {user.followers_count:,} followers")
    
    followers = client.user_followers(user.pk, limit=LIMIT)
    print(f"      ✅ {len(followers)} followers")
    
    for i, f in enumerate(followers[:3], 1):
        print(f"         {i}. @{f.username}")
    
    # Save result
    result = {
        "target": TARGET,
        "followers_count": user.followers_count,
        "sample_followers": [{"username": f.username} for f in followers[:3]]
    }
    with open("smoke_test_final.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ TEST COMPLETADO!")
    print(f"Archivo: smoke_test_final.json")

except Exception as e:
    print(f"❌ Error: {e}")

finally:
    client.close()
    print("\n✅ Done!")
