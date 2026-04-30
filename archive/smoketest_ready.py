"""
✅ SMOKE TEST - INSTAGRAM SCRAPING + FIRECRAWL
"""

from instagrapi import Client
from firecrawl import FirecrawlApp
import time
import re
import json

# === CONFIG ===
USERNAME = "ValesNissanCombustible"
PASSWORD = "20063288"
TARGET = "clinicavesaliooficial"
FIRECRAWL_API = "fc-14caab385b0a45358487da709d1a5fb9"

# === PASO 1: SessionID Manual ===
# Carga este archivo o pon el sessionid en la consola
try:
    with open("smoke_test.json", "r") as f:
        sessionid = json.load(f).get("sessionid", "")
elif open("smoke_test.json", "w") as f:
    json.dump({"sessionid": "PONE_TU_SESSIONID_AQUI"}, f)
    sessionid = "PONE_TU_SESSIONID_AQUI"
else:
    sessionid = "sessionid_temp"

# === SETUP ===
print("="*60)
print("🚀 FINAL SMOKE TEST - Instrucciones")
print("="*60)
print(f"\n1. Editando sessionid a: {sessionid[:30]}...")

client = Client()

# Try direct web login first
print("\nStep 1: Create client & Pre-flow...")
try:
    client.sessionid = sessionid
    client.mid = "mid_"
    client.pre_login_flow()
    print("   ✅ OK")
except Exception as e:
    print(f"   ⚠️ Warning: {e}")

# === 2) WEB FLW LOGIN (if needed) ===
print("\nStep 2: Test Login...")
try:
    client.login(USERNAME, PASSWORD)
    print("   ✅ Login Success!")
except Exception as e:
    print(f"   ⚠️ Login: {type(e).__name__}")
    # Fallback to web session
    try:
        client.sessionid = "web_session_mode"
        print("   → Fallback: Web Session Mode")
    except:
        pass

# === 3) TEST USER INFO ===
print(f"\nStep 3: User Info Test: @{TARGET}")
try:
    user = client.user_info_by_username(TARGET)
    print(f"   ✅ User: {user.username}")
    print(f"   ✅ ID: {user.pk}")
    print(f"   ✅ Followers: {user.followers_count:,}")
    
    # Get followers
    print(f"\nStep 4: Followers ({TARGET}...")
    followers = client.user_followers(user.pk, limit=10)
    print(f"   ✅ {len(followers)} followers")
    
    with open("instagram_sample_followers.json", "w") as f:
        json.dump({
            "target": TARGET,
            "followers_count": user.followers_count,
            "samples": [{"username": f.username, "pk": f.pk} for f in followers[:3]]
        }, f, indent=2)
    print(f"   ✅ Saved: instagram_sample_followers.json")
    
except Exception as e:
    print(f"   ⚠️ Error: {e}")

# === 4) FIRECRAWL ===
print(f"\nStep 5: Firecrawl - Scrape Website...")
try:
    app = FirecrawlApp(api_key=FIRECRAWL_API)
    
    if hasattr(user, 'website') and user.website:
        print(f"   Website: {user.website}")
        
        sc = app.scrape_url(user.website, params={"formats": ["markdown"]})
        md = sc.get("markdown", "")
        
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', md)
        
        print(f"   ✉️ Emails Found: {len(emails)}")
        
        result = {
            "target": TARGET,
            "website": user.website,
            "emails": emails,
            "preview": md[:200]
        }
        
        with open("firecrawl_result.json", "w") as f:
            json.dump(result, f, indent=2)
        print(f"   ✅ Saved: firecrawl_result.json")
    
except Exception as e:
    print(f"   ⚠️ Error: {type(e).__name__}: {e}")

# === 5) FINAL ===
print(f"\n{'='*60}")
print("✅ TEST COMPLETED!")
print(f"{'='*60}")
print(f"   Files: instagram_sample_followers.json, firecrawl_result.json")
print(f"   Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

client.close()
input("\nPress ENTER to exit...")
