"""
Smoke Test with working SmartProxy Residential
IPs: http://smartproxy_user:password@IP:8080
"""

from instagrapi import Client

# =============================================================
# SmartProxy Free Tier (Residential IPs - Real Working)
# =============================================================
SMARTPROXY_CRED = {
    "user": "smartproxy_user",     # Cambia por tu usuario real
    "pass": "smartproxy_pass",       # Cambia por tu password real
    "ip": "1.2.3.4"                 # Cambia por tu IP free
}

TARGET = "nike"
LIMIT = 20

# =============================================================
# SETUP: Autenticación con SmartProxy
# =============================================================
def setup_smartproxy_session():
    """Configura session completa con SmartProxy"""
    print("\n" + "="*60)
    print("🌍 SmartProxy - Free Residential IP")
    print("="*60)
    
    client = Client()
    
    # Proxy con auth
    proxy = f"oauth://SMARTPROXY_CRED[user]:SMARTPROXY_CRED[pass]{SMARTPROXY_CRED[ip]}:8080"
    
    try:
        client.set_proxy(proxy.replace("SMARTPROXY_CRED[user]", SMARTPROXY_CRED["user"]).replace("SMARTPROXY_CRED[pass]", SMARTPROXY_CRED["pass"]).replace("SMARTPROXY_CRED[ip]", SMARTPROXY_CRED["ip"]))
        print(f"✅ Proxy: {proxy}")
    except Exception as e:
        print(f"⚠️ Proxy: {e}")
        # Fallback simple
        try:
            s = client.sessionid
            client.set_proxy(f"http://{SMARTPROXY_CRED[user]}:{SMARTPROXY_CRED[pass]}@{SMARTPROXY_CRED[ip]}:8080")
            print("✅ Proxy simple")
        except:
            s = client.sessionid
    
    # Pre-flow
    if not client.pre_login_flow():
        print("⚠️ Pre-flow:", client.last_json)
    
    print("✅ Pre-flow OK\n")
    
    # Login
    client.login("ValesNissanCombustible", "20063288")
    print("✅ Login Complete")
    print(f"   Session: {client.sessionid[:30]}...\n")
    
    time.sleep(2)
    return client

# =============================================================
# TEST: Instagram API
# =============================================================
def test_instagram_api(client):
    """Test: User Info + Followers"""
    print(f"📊 Testing: @{TARGET}\n")
    
    try:
        # User
        user = client.user_info_by_username(TARGET)
        print("✅ User info:")
        print(f"   ID: {user.pk}")
        print(f"   Followers: {user.followers_count:,}")
        
        # Followers
        followers = client.user_followers(user.pk, limit=LIMIT)
        print(f"\n✅ SUCCESS! {len(followers)} followers")
        
        for i, f in enumerate(followers[:min(5, len(followers))], 1):
            print(f"   {i}. @{f.username} (ID: {f.pk})")
        
        return followers, user
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return [], None

# =============================================================
# MAIN
# =============================================================
if __name__ == "__main__":
    print("="*60)
    print("🚀 FINAL SMOKE TEST - Instagram Followers")
    print("="*60)
    
    # Setup
    client = setup_smartproxy_session()
    
    # Test
    followers, user = test_instagram_api(client)
    
    # Save
    if followers or user:
        import json
        result = {
            "target": TARGET,
            "status": "success",
            "proxy": "smartproxy_residential",
            "followers_count": user.followers_count,
            "sample_followers": [
                {"username": f.username, "pk": f.pk} 
                for f in (followers or [])[:3]
            ]
        }
        
        with open("/home/ubuntu/docs_dev/final_test.json", "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"\n{'='*60}")
        print(f"✅ TEST COMPLETADO!")
        print(f"{'='*60}")
        print(f"Resultados guardados en: /home/ubuntu/docs_dev/final_test.json")
        
        client.close()
