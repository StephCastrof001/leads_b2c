"""
Smoke Test V2 - Instagram Followers Extractor
Métodos: 1) Proxy free (Squid)
         2) Session ID manual (desde navegador)
"""

from instagrapi import Client
import json
import time
import getpass

# ============================================================
# METODO 1: con Proxy Free (Squid)
# ============================================================
def method_proxy(squid_proxy="127.0.0.1:3128"):
    """Usa proxy local squid (free tier)"""
    print("\n" + "="*60)
    print("🔥 MÉTODO 1: Proxy Free (Squid - 127.0.0.1:3128)")
    print("="*60)
    
    client = Client()
    
    # Setear proxy squid (free)
    print(f"   Setting proxy: {squid_proxy}")
    try:
        client.set_proxy(squid_proxy)
        print("   ✅ Proxy configured")
    except Exception as e:
        print(f"   ⚠️ Proxy error: {e}")
        print("      (Continuando sin proxy auto...")
    
    # Pre-flow
    print("\n   1. Pre-flow...")
    result = client.pre_login_flow()
    if not result:
        print(f"   Result: {result}")
        return None
    
    # Login (con credentials)
    print("\n   2. Login con credentials...")
    try:
        result = client.login("ValesNissanCombustible", "20063288")
        print(f"   Result: {result}")
        return client or Client()
    except Exception as e:
        print(f"   Login error: {type(e).__name__}: {e}")
        return client

# ============================================================
# METODO 2: con Session ID Manual
# ============================================================
def method_session(session_file=None):
    """Usa sessionid guardado en archivo json"""
    print("\n" + "="*60)
    print("🔧 MÉTODO 2: Session ID Manual")
    print("="*60)
    
    if not session_file:
        session_file = "/home/ubuntu/docs_dev/instagram_session.json"
    
    print(f"   Cargando session desde: {session_file}")
    
    client = Client()
    
    try:
        if session_file and False:  # Habilita si tienes archivo
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            client.sessionid = session_data.get('sessionid')
            if client.sessionid:
                print(f"   ✅ Session cargada: {client.sessionid[:30]}...")
                return client
        else:
            print("   (Sin archivo de session, creando nuevo...)")
            client.pre_login_flow()
            
    except Exception as e:
        print(f"   ⚠️ Error cargando session: {e}")
    
    print("   2. Login con session web...")
    return client

# ============================================================
# TEST PRINCIPAL: Obtener seguidores
# ============================================================
def test_followers(client, target="nike", limit=10):
    """Test final: obtener info + seguidores"""
    print(f"\n   📊 Testing: @{target}")
    
    if not client or not client.get('private') or not client.get('public'):
        print("   ❌ Client no está autenticado correctamente")
        return []
    
    try:
        print("   1. Obteniendo user info...")
        user = client.user_info_by_username(target)
        
        print(f"   ✅ User encontrado:")
        print(f"      ID: {user.pk}")
        print(f"      Followers: {user.followers_count:,}")
        print(f"      Following: {user.following_count:,}")
        print(f"      Posts: {user.media_count:,}")
        
        print(f"\n   2. Obteniñendo {limit} seguidores...")
        followers = client.user_followers(user.pk, limit=limit)
        
        print(f"   ✅ Followers list: {len(followers)} encontrados")
        for i, f in enumerate(followers[:min(5, len(followers))], 1):
            print(f"      {i}. @{f.username} (ID: {f.pk})")
        
        return followers, user
        
    except Exception as e:
        print(f"   ⚠️ Error en test: {type(e).__name__}: {e}")
        # Intento fallback
        try:
            print("   → Fallback: web_profile_info...")
            user2 = client.web_profile_info(target)
            print(f"   ✅ User2: {user2.username}, {user2.followers_count:,} followers")
            return [], user2
        except Exception as e2:
            print(f"   → Fallback error: {e2}")
            return [], None

# ============================================================
# MAIN: Ejecutar ambos métodos
# ============================================================
def main():
    print("="*60)
    print("🚀 SMOK TEST V2 - Instagram Followers Extractor")
    print("="*60)
    
    # Método 1: Proxy
    print("\n🔥 TEST MÉTODO 1 (Proxy)...")
    proxy_client = method_proxy(squid_proxy="127.0.0.1:3128")
    followers1, user1 = test_followers(proxy_client, "nike")
    
    if followers1 or user1:
        print(f"   🎉 Método 1: {'SUCCESS' if followers1 else 'PARTIAL'} - {len(followers1) if followers1 else 'User found'} found")
    else:
        print(f"   ⚠️ Método 1: Failed")
    
    # Método 2: Session
    if followers1 or user1:
        print("\n🔧 TEST MÉTODO 2 (Session)...")
        session_client = method_session()
        followers2, user2 = test_followers(session_client, "nike")
        
        if followers2 or user2:
            print(f"   🎉 Método 2: {'SUCCESS' if followers2 else 'PARTIAL'} - {len(followers2) if followers2 else 'User found'} found")
    
    # Guardar resultados
    import json
    result = {
        "target": "nike",
        "method1_fallbacks_proxies": (followers1 == followers2 if followers1 else "unknown")
    }
    
    with open("/home/ubuntu/docs_dev/smoke_test_v2_results.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n{'='*60}")
    print("✅ TEST COMPLETADO!")
    print(f"{'='*60}")
    
    if proxy_client:
        proxy_client.close()

if __name__ == "__main__":
    main()
