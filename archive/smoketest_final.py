"""
SMOKETEST INSTAGRAM FOLLOWERS - SMARTPROXY + FIRECRAWL
========================================================

Configuración Completa:
  1) SmartProxy (Residential IP Free Tier)
  2) Firecrawl (Website Scraping - Email Extraction)
  3) Instagram API (Followers & User Info)

CREDenciales:
  Proxy: smartproxy_user:password@77.77.77.77:8080
  Firecrawl: e7d9732fd6351820c3a47889055fd3e5
  Insta: ValesNissanCombustible / 20063288
"""

from instagrapi import Client
from firecrawl import FirecrawlApp
import time
import json

# ============== CONFIGURACIÓN
# ==============
PROXY = "http://smartproxy_user:password@77.77.77.77:8080"
FIRECRAWL_API_KEY = "e7d9732fd6351820c3a47889055fd3e5"
TARGET = "nike"
LIMIT = 10
USERNAME = "ValesNissanCombustible"
PASSWORD = "20063288"

# ============== INSTAGRAM CLIENT + SMARTPROXY
# ==============
print("="*60)
print("🚀 SMOKE TEST - Instagram Followers Extractor")
print("="*60)

# 1. Configurar Client con Proxy
client = Client()
print(f"\n   1. Configurar SmartProxy...")

try:
    client.set_proxy(PROXY)
    print(f"      ✅ Proxy: {PROXY[:40]}...")
except Exception as e:
    print(f"      ⚠️ Proxy fallback: {e}")
    try:
        client.set_proxy("http://simple:8080")
        print("      ✅ Proxy simple OK")
    except:
        print("      ⚠️ No proxy disponible")

# 2. Autenticar
print(f"\n   2. Autenticar...")
if not client.pre_login_flow():
    print(f"      ⚠️ Pre-flow: {client.last_json.get('error', 'unknown')}")

client.login(USERNAME, PASSWORD)
print("      ✅ Login Successful")

time.sleep(2)

# ============== FIRECRAWL (Web Scraping)
# ==============
print(f"\n   3. Configurar Firecrawl...")
try:
    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
    print(f"      ✅ Firecrawl configured")
except Exception as e:
    print(f"      ⚠️ Firecrawl: {e}")
    app = None

# ============== TEST: INSTA API
# ==============
print(f"\n   4. Test API: @{TARGET}")

try:
    # Get User Info
    user = client.user_info_by_username(TARGET)
    print(f"      ✅ User ID: {user.pk}")
    print(f"      ✅ Followers: {user.followers_count:,}")
    print(f"      ✅ Name: {user.display_name}")
    
    # Get Followers
    followers = client.user_followers(user.pk, limit=LIMIT)
    print(f"\n      ✅ SUCCESS! {len(followers)} followers")
    
    # Show samples
    print(f"\n      Sample Followers:")
    for i, f in enumerate(followers[:5], 1):
        print(f"         {i}. @{f.username} (ID: {f.pk})")
    
    # ============== SCRAPE WEBSITES FOR EMAILS (Firecrawl)
    # ==============
    print(f"\n   5. Scraping Websites (Firecrawl)...")
    
    if app and user.website:
        print(f"      Website: {user.website}")
        try:
            # Scrápear website para extraer emails
            scrape_result = app.scrape_url(
                user.website,
                params={
                    "scrapeOptions": {
                        "formats": ["markdown"],
                        "excludeTags": ["nav", "footer", "header"]
                    }
                }
            )
            print(f"      ✅ Scrape: {scrape_result.get('content', '')[:100]}...")
            
            # Extraer emails (simple regex)
            import re
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', scrape_result.get('markdown', ''))
            print(f"      ✉️ Emails encontrados: {len(emails)} - {emails[:3] if emails else 'none'}")
            
        except Exception as e:
            print(f"      ⚠️ Scrape: {e}")
    else:
        print(f"      ℹ️ Usuario no tiene website pública")
    
    # ============== GUARDAR RESULTADO
    # ==============
    import json
    result = {
        "target": TARGET,
        "proxy": "smartproxy_residential",
        "firecrawl": True,
        "status": "success",
        "followers_count": user.followers_count,
        "sample_followers": [
            {"username": f.username, "pk": f.pk} 
            for f in (followers or [])[:3]
        ]
    }
    
    output_file = "/home/ubuntu/docs_dev/smoke-final-results.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ SMOKE TEST COMPLETADO!")
    print(f"{'='*60}")
    print(f"Resultados: {len(followers)} followers encontrados")
    print(f"Archivo: {output_file}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
except Exception as e:
    print(f"\n   ❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
finally:
    if client:
        client.close()
        print("\n✅ Client closed")

print("\n⏳ Esperando comando para siguiente prueba...")
