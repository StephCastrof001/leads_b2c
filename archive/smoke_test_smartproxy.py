"""
Smoke Test con SmartProxy Residential (Free Tier Trial)
Configuración: SmartProxy Free IP + Authentication
"""

from instagrapi import Client
import time

# ============================================================
# SmartProxy Free Trial (Residential IPs)
# ============================================================
SMARTPROXY_CONFIG = {
    "host": "proxy-smartproxy.net",  # IP free trial
    "port": "8080",
    "user": "smartproxy_user",  # Cambia por tu usuario
    "password": "smartproxy_pass"  # Cambia por tu password
}

# Opción alternativa: IP directa (si SmartProxy ya lo tiene activo)
DIRECT_PROXY_RESIDENTIAL = {
    "username": "smartproxy_user", 
    "password": "smartproxy_pass",
    "ip": "77.77.77.77",  # IP residencial del trial
    "port": "8080"
}

# ============================================================
# CONFIGURACIÓN CREDenciales
# ============================================================
CREDENTIALS = {
    "username": "ValesNissanCombustible",
    "password": "20063288"
}

TARGET = "nike"
LIMIT = 20

# ============================================================
# METODO SMARTPROXY: Con IP Residencial Real
# ============================================================
def setup_smartproxy_session():
    """Configura session con SmartProxy Residential"""
    print("\n" + "="*60)
    print("🌍 SmartProxy FREE TRIAL - Residensial IP")
    print("="*60)
    
    client = Client()
    
    # Configurar proxy con auth
    print("   1. Configurar proxy SmartProxy...")
    proxy_auth = f"oauth://smartproxy_user:smartproxy_pass@77.77.77.77:8080"
    
    try:
        client.set_proxy(proxy_auth)
        print(f"      ✅ Proxy set: {proxy_auth[:40]}...")
    except Exception as e:
        print(f"      ⚠️ Proxy auth: {e}")
        # Fallback: prox simple
        try:
            client.set_proxy(f"http://smartproxy_user:smartproxy_pass@77.77.77.77:8080")
            print(f"      ✅ Proxy simple set")
        except:
            print(f"      ⚠️ Proxy simple failed")
    
    # Pre-flow
    print("\n   2. Pre-flow...")
    if not client.pre_login_flow():
        print(f"      ⚠️ Pre-flow: {client.last_json}")
        return [], client
    
    print(f"      ✅ Pre-flow OK")
    
    # Login
    print("\n   3. Login flow...")
    try:
        result = client.login(CREDENTIALS["username"], CREDENTIALS["password"])
        print(f"      ✅ Login: {result}")
        print(f"      Session ID: {getattr(client, 'sessionid', 'N/A')[:30]}...")
    except Exception as e:
        print(f"      ⚠️ Login: {type(e).__name__}")
        
        # Fallback: usar web_flow (interactivo)
        print("\n      → Fallback: Web flow (browser)?")
        try:
            result = client.web_flow(
                data={"username": CREDENTIALS["username"], "password": CREDENTIALS["password"]},
                browser_type="chrome"
            )
            print(f"      ✅ Web flow: {result}")
        except Exception:
            print(f"      ⚠️ Web flow falló")
    
    time.sleep(2)
    return [], client

# ============================================================
# METODO MANUAL: Session ID desde Navegador
# ============================================================
def setup_manual_session():
    """Usa sessionid manual desde https://app.instagram.com/challenge/"""
    print("\n" + "="*60)
    print("🔧 SESSION MANUAL - Desde Browser")
    print("="*60)
    print("""
   1. Abre este link en navegador:
      https://app.instagram.com/challenge/?flow=web_flow_consent
   
   2. Ingresa tus credentials
   3. Luego obtén el sessionid de la cookie (Ctrl+Shift+I -> Network -> Headers)
      Cookie name: "sessionid" value: "ABCdef123..."
   
   4. Presiona ENTER en el script para confirmar el sessionid
   """)
    
    input("   4. Presiona ENTER cuando tengas un sessionid válido...")
    
    client = Client()
    sessionid = input("   > Session ID: ").strip()
    
    # Guardar session
    session_data = {
        "sessionid": sessionid,
        "mid": "aeuRhgABAAHzaGKyK2Tii4gHRj4d...",  # Generar o copiar
        "tray_session_id": "240610bf-5407-4175-862b-7dfdd6b73c27"
    }
    
    if sessionid:
        client.sessionid = sessionid
        print(f"   ✅ Session loaded: {sessionid[:20]}...")
    
    # Pre-flow
    print("\n   5. Pre-flow...")
    if not client.pre_login_flow():
        print(f"      ⚠️ Pre-flow: {client.last_json}")
        return [], client
    
    print(f"      ✅ Pre-flow OK")
    
    # Login con session
    print("\n   6. Login con session...")
    try:
        result = client.login(CREDENTIALS["username"], CREDENTIALS["password"])
        print(f"      ✅ Login: {result}")
    except Exception as e:
        print(f"      ⚠️ Login: {type(e).__name__}")
    
    time.sleep(2)
    return [], client

# ============================================================
# TEST FINAL
# ============================================================
def run_final_test(client):
    """Ejecuta test completo con la sesión"""
    print(f"\n   7. Test: @{TARGET}")
    print("      Subtest: User info + Followers...")
    
    followers = []
    user = None
    
    try:
        # 1. Info usuario
        print(f"      Subtest 1: User info...")
        user = client.user_info_by_username(TARGET)
        
        print(f"         ✅ User ID: {user.pk}")
        print(f"         ✅ Followers: {user.followers_count:,}")
        print(f"         ✅ Display: {user.display_name}")
        
        # 2. Followers
        print("\n      Subtest 2: Followers (limit: {})...".format(LIMIT))
        followers = client.user_followers(user.pk, limit=LIMIT)
        
        print(f"         ✅ SUCCESS! Total: {len(followers)}")
        print(f"\n         Samples:")
        for i, f in enumerate(followers[:min(3, len(followers))], 1):
            print(f"            {i}. @{f.username} (ID: {f.pk})")
        
        return followers, user
        
    except Exception as e:
        print(f"   ⚠️ Error: {type(e).__name__}: {e}")
        return [], None

# ============================================================
# MAIN - PRIMER METODO: SmartProxy
# ============================================================
def main_smartproxy():
    print("="*60)
    print("🚀 SMOKE TEST SMARTPROXY - Instagram Followers")
    print("="*60)
    
    try:
        setup_smartproxy_session()
        followers, user = run_final_test(client)
        
        # Guardar resultados
        if followers or user:
            import json
            result = {
                "target": TARGET,
                "status": "success",
                "proxy": "smartproxy_residential",
                "followers_count": user.followers_count if user else None,
                "sample_followers": [
                    {"username": f.username, "pk": f.pk} 
                    for f in (followers or [])[:3]
                ]
            }
            
            with open("/home/ubuntu/docs_dev/smoke_test_smartproxy.json", "w") as f:
                json.dump(result, f, indent=2)
            
            print(f"\n{'='*60}")
            print(f"✅ SMART PROXY TEST COMPLETADO!")
            print(f"{'='*60}")
            print(f"Resultados: {len(followers)} followers encontrados")
            print(f"Archivo: /home/ubuntu/docs_dev/smoke_test_smartproxy.json")
            
            if hasattr(client, 'close'):
                client.close()
            
            return True
        else:
            print("\n   ⚠️ SmartProxy test parcial")
            return False
            
    except Exception as e:
        print(f"\n   ⚠️ SmartProxy error: {type(e).__name__}: {e}")
        return False

# ============================================================
# MAIN - SEGUNDO METODO: Session Manual
# ============================================================
def main_manual():
    print("="*60)
    print("🔧 SMOKE TEST SESSION MANUAL - Instagram Followers")
    print("="*60)
    
    try:
        setup_manual_session()
        followers, user = run_final_test(client)
        
        # Guardar resultados
        if followers or user:
            import json
            result = {
                "target": TARGET,
                "status": "success",
                "session": "manual_web",
                "followers_count": user.followers_count if user else None,
                "sample_followers": [
                    {"username": f.username, "pk": f.pk} 
                    for f in (followers or [])[:3]
                ]
            }
            
            with open("/home/ubuntu/docs_dev/smoke_test_manual.json", "w") as f:
                json.dump(result, f, indent=2)
            
            print(f"\n{'='*60}")
            print(f"✅ MANUAL SESSION TEST COMPLETADO!")
            print(f"{'='*60}")
            print(f"Resultados: {len(followers)} followers encontrados")
            print(f"Archivo: /home/ubuntu/docs_dev/smoke_test_manual.json")
            
            if hasattr(client, 'close'):
                client.close()
            
            return True
        else:
            print("\n   ⚠️ Manual session test parcial")
            return False
            
    except Exception as e:
        print(f"\n   ⚠️ Manual error: {type(e).__name__}: {e}")
        return False

# ============================================================
# MAIN EXEC
# ============================================================
if __name__ == "__main__":
    print("Elige método:")
    print("   1) SmartProxy Free Trial (IP residencial) - AUTO")
    print("   2) Session ID Manual (desde Browser) - INTERACTIVO")
    
    choice = input("\n   Elige (1/2): ").strip()
    
    if choice == "1":
        main_smartproxy()
    elif choice == "2":
        main_manual()
    else:
        print("   Default: SmartProxy")
        main_smartproxy()
