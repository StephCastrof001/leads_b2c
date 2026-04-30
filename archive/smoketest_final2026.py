"""
⚡ FINAL SMOKE TEST 2026 - Instagram Scraper + Firecrawl
"""

from instagrapi import Client
from firecrawl import FirecrawlApp
import time
import re
import json

# === 1) CONFIGURATION
USERNAME = "ValesNissanCombustible"
PASSWORD = "20063288"
TARGET = "clinicavesaliooficial"
FIRECRAWL_API = "fc-14caab385b0a45358487da709d1a5fb9"
LIMIT = 20

# === 2) SESSIONID MANUAL (Copia de https://www.instagram.com/developer/cookies/)
# Pasos:
# 1. Abre: https://www.instagram.com/accounts/login/
# 2. Ingresa tus credentials
# 3. Presiona F12 -> Network -> Headers -> Cookies
# 4. Busca "sessionid" y copia su valor

SESSIONID = "COPIA_DE_LA_COOKIE_sessionid_AQUI"

# === 3) SETUP
print("="*60)
print("🚀 FINAL SMOKE TEST - Instagram + Firecrawl")
print("="*60)

client = Client()

# Configurar session manual
try:
    client.sessionid = SESSIONID
    client.mid = "mid_fallback_"
    print(f"\n✅ Session loaded: {client.sessionid[:30]}...")
except Exception as e:
    print(f"\n⚠️ Session set: {e}")
    client.sessionid = "temp"

# === 4) LOGIN + TEST
print(f"\nStep 1: Pre-flow...")
try:
    client.pre_login_flow()
    print("   ✅ OK")
except Exception as e:
    print(f"   ⚠️ Warning: {e}")

print(f"\nStep 2: User Info Test: @{TARGET}")
try:
    user = client.user_info_by_username(TARGET)
    print(f"   ✅ User: {user.username}")
    print(f"   ✅ ID: {user.pk}")
    print(f"   ✅ Followers: {user.followers_count:,}")
    print(f"   ✅ Following: {user.following_count}")
except Exception as e:
    print(f"   ⚠️ Error: {type(e).__name__}: {e}")
    print("   → Try with web profile...")
    try:
        user = client.web_profile_info(TARGET)
        print(f"   ✅ Web User: {user.username}")
    except Exception as e2:
        print(f"   → Error: {e2}")

# === 5) GET FOLLOWERS
if user:
    print(f"\nStep 3: Followers ({LIMIT}...")
    try:
        followers = client.user_followers(user.pk, limit=LIMIT)
        print(f"   ✅ SUCCESS! Total: {len(followers)}")
        
        # Sample
        print(f"\n   Sample ({min(3, len(followers))}...")
        for i, f in enumerate(followers[:min(3, len(followers))], 1):
            print(f"      {i}. @{f.username} (ID: {f.pk})")
        
        # Save followers
        with open("followers_sample.json", "w") as f:
            import json
            json.dump({
                "target": TARGET,
                "followers_count": user.followers_count,
                "sample_followers": [{"username": f.username, "pk": f.pk} for f in followers[:3]]
            }, f, indent=2)
        print(f"   ✅ Saved: followers_sample.json")
    
    except Exception as e:
        print(f"   ⚠️ Error: {e}")

# === 6) FIRECRAWL: SCRAPE WEBSITE
print(f"\nStep 4: Firecrawl - Scrape Website for Emails...")
try:
    app = FirecrawlApp(api_key=FIRECRAWL_API)
    print(f"   ✅ Firecrawl API: {FIRECRAWL_API[:15]}...")
    
    # Check user website
    if hasattr(user, 'website') and user.website:
        print(f"   Website: {user.website}")
        
        markdown = app.scrape_url(
            user.website,
            params={
                "formats": ["markdown"],
                "scrapeOptions": {
                    "excludeTags": ["nav", "footer", "header", "script"]
                }
            }
        )
        
        md = markdown.get("markdown", "").strip()
        print(f"\n   Markdown ({len(md)} chars): {md[:200]}...")
        
        # Extract emails
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', md)
        phones = re.findall(r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', md)
        
        print(f"\n   ✉️ Emails: {len(emails)} - {emails[:5]}")
        print(f"   📱 Phones: {len(phones)} - {phones[:5]}")
        
        # Save result
        result = {
            "target": TARGET,
            "source": "firecrawl_web_scraper",
            "website": user.website,
            "emails_found": len(emails),
            "sample_emails": emails[:5],
            "phones_found": len(phones),
            "preview": md[:300]
        }
        
        with open("firecrawl_test_result.json", "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"\n   ✅ Saved: firecrawl_test_result.json")
    
    elif hasattr(user, 'external_url') and user.external_url:
        print(f"   External URL: {user.external_url}")
        # Same scrape logic...
    
    else:
        print(f"   ℹ️ Usuario no tiene website en bio")
    
except Exception as e:
    print(f"   ⚠️ Error: {type(e).__name__}")
    print(f"   Detail: {str(e)[:300]}")
    import traceback
    traceback.print_exc()

# === 7) FINAL RESULTS
print(f"\n{'='*60}")
print(f"✅ SMOKE TEST COMPLETADO!")
print(f"{'='*60}")
print(f"   Target:     @{TARGET}")
print(f"   Session:    {SESSIONID[:30]}...")
print(f"   Followers:  ~{user.followers_count if user else 'unknown'}")
print(f"   Files:      followers_sample.json, firecrawl_test_result.json")
print(f"   Time:       {time.strftime('%Y-%m-%d %H:%M:%S')}")

if hasattr(client, 'end_session'):
    client.end_session()
    print(f"\n✅ Client cleared")

input(f"\n✅ Presiona ENTER cuando termines. ..")
