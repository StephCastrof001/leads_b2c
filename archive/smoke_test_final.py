"""
Smoke Test FINAL - Instagram Followers Extractor
Estrategia flexible:
  1) Intentar sin proxy (directo)
  2) Intentar con proxy (fallback)
  3) Usar session manual (último recurso)
"""

from instagrapi import Client
import time

# ============================================================
# CONFIGURACIÓN FLEXIBLE
# ============================================================
PROXIES_CONFIG = {
    "default": None,           # Sin proxy (directo)
    "squid": "127.0.0.1:3128", # Proxy Squid free
    "smartproxy": "smartproxy:password@1.2.3.4:8080" # SmartProxy
}

CREDENTIALS = {
    "username": "ValesNissanCombustible",
    "password": "20063288"
}

TARGET = "nike"
LIMIT = 10

# ============================================================
# METODO 1: Sin Proxy (Directo con pre_login_flow + login_flow)
# ============================================================
def method_direct():
    """Método 1: Directo (sin proxy)"""
    print("\n" + "="*60)
    print("🔥 MÉTODO 1: Directo (Sin Proxy)")
    print("="*60)
    
    client = Client()
    
    # 1. Pre-flow
    print("   1. Pre-flow...")
    if not client.pre_login_flow():
        print("      ⚠️ Pre-flow falló")
        return []
    
    print("      ✅ Pre-flow OK")
    
    # 2. Login flow (interactivo)
    print("   2. Login flow (browser interactivo)...")
    try:
        # Esto abrirá el navegador para confirmar el login
        result = client.login_flow()
        print(f"      Result: {result}")
        
        time.sleep(2)
        
        # 3. Test: obtener usuario
        print("   3. Test: Obteniendo user info...")
        user = client.user_info_by_username(TARGET)
        print(f"      ✅ User ID: {user.pk}")
        print(f"      ✅ Followers: {user.followers_count:,}")
        
        # 4. Test: obtener seguidores
        print("   4. Test: Obteniñendo seguidores...")
        followers = client.user_followers(user.pk, limit=LIMIT)
        
        print(f"   ✅ SUCCESS: {len(followers)} followers encontrados")
        print("\n   Sample followers:")
        for i, f in enumerate(followers[:min(5, len(followers))], 1):
            print(f"      {i}. @{f.username} (ID: {f.pk})")
        
        return followers, user
        
    except Exception as e:
        print(f"   ⚠️ Error: {type(e).__name__}: {e}")
        return [], None

# ============================================================
# METODO 2: Con Proxy (Squid Free)
# ============================================================
def method_squid():
    """Método 2: Proxy Squid"""
    print("\n" + "="*60)
    print("🔄 MÉTODO 2: Proxy Squid")
    print("="*60)
    
    proxy = PROXIES_CONFIG.get("squid")
    print(f"   Proxy: {proxy}")
    
    client = Client()
    
    # Set proxy
    try:
        client.set_proxy(proxy)
        print("   ✅ Proxy set")
    except Exception as e:
        print(f"   ⚠️ Proxy set: {e}")
    
    # Pre-flow
    try:
        if not client.pre_login_flow():
            raise Exception("Pre-flow fail")
        print("   ✅ Pre-flow OK")
    except Exception:
        print("   ⚠️ Pre-flow fallback, trying direct...")
        client.set_proxy(None)
        if not client.pre_login_flow():
            return []
        print("   ✅ Direct pre-flow OK")
    
    # Login
    try:
        result = client.login(CREDENTIALS["username"], CREDENTIALS["password"])
        print(f"   ✅ Login: {result}")
    except Exception:
        print("   ⚠️ Login fallback...")
    
    # Test
    try:
        user = client.user_info_by_username(TARGET)
        print(f"   ✅ User: {user.pk} - {user.display_name}")
        print(f"   ✅ Followers: {user.followers_count:,}")
        
        followers = client.user_followers(user.pk, limit=LIMIT)
        print(f"   ✅ SUCCESS: {len(followers)} followers")
        
        for i, f in enumerate(followers[:min(5, len(followers))], 1):
            print(f"      {i}. @{f.username}")
        
        return followers, user
        
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
        return [], None

# ============================================================
# MAIN: Ejecutar todos los métodos
# ============================================================
def main():
    print("="*60)
    print("🚀 SMOKE TEST FINAL - Instagram Followers Extractor")
    print("="*60)
    print(f"\nTarget: @{TARGET}")
    print(f"Creds: {CREDENTIALS['username']}")
    print(f"Limit: {LIMIT} followers")
    
    # ============================================================
    # TEST 1: Directo
    # ============================================================
    result1 = method_direct()
    if result1[0] or result1[1]:
        print("\n🎉 METODO 1 SUCCESS!")
        
        # Guardar resultados
        import json
        followers, user = result1
        result = {
            "target": TARGET,
            "followers_count": user.followers_count,
            "sample_followers": [{"username": f.username, "pk": f.pk} for f in followers[:3]]
        }
        
        with open("/home/ubuntu/docs_dev/smoke_test_final.json", "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"\nResultados guardados en: smoke_test_final.json")
        print("\n" + "="*60)
        print("✅ TEST COMPLETADO EN MÉTODO 1")
        print("="*60)
    
        if hasattr(result1[0], 'close'):
            result1[0].close()
        return result1
    
    # ============================================================
    # TEST 2: Con Proxy
    # ============================================================
    print("\nContinuando con MÉTODO 2 (Proxy Squid)...")
    result2 = method_squid()
    
    if result2[0] or result2[1]:
        print("\n🎉 METODO 2 SUCCESS!")
    
    return result2 if result2[0] or result2[1] else result1

if __name__ == "__main__":
    main()
