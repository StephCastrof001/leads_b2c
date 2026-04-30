"""
Smoke Test con Session ID real (guardada desde navegador)
Opción: Usar sessionid que ya tenemos pre-generada
"""

from instagrapi import Client
import json

# ============================================================
# CARGAR SESSION PRE-GuardADA
# ============================================================
def load_pre_saved_session():
    """Carga sessionid guardada"""
    print("\n" + "="*60)
    print("🔧 METODO: Session ID Pre-Guardada")
    print("="*60)
    
    print("   1. Buscando archivo de session...")
    
    files = [
        "/home/ubuntu/docs_dev/instagram_session.json",
        "/home/ubuntu/docs_dev/smoke_test.json",
        "/tmp/instagram_session.json"
    ]
    
    client = Client()
    
    found = False
    for f in files:
        try:
            if found:
                break
            with open(f, 'r') as file:
                session_data = json.load(file)
                print(f"      ✅ Found: {f}")
                
                # Extraer sessionid
                if isinstance(session_data, dict):
                    sessionid = session_data.get('sessionid') or session_data.get('session_id')
                else:
                    sessionid = str(session_data)[:50]
                
                if sessionid:
                    print(f"   ✅ Session ID: {sessionid[:30]}...")
                    client.sessionid = sessionid
                    found = True
                    break
                print(f"   ⚠️ Session data minimal")
                
        except Exception as e:
            print(f"      ⚠️ Error: {f}: {e}")
    
    if not found:
        print("   ⚠️ No se encontró session activa")
        # Crear nueva session (pre-flow)
        print("\n   2. Creando nueva session (pre-flow)...")
        client.pre_login_flow()
        # Guardar para usar después
        session_data = {
            "preflow": True,
            "time": "2026-04-24 05:45",
            "attrs": {k: str(v)[:30] for k, v in client.__dict__.items() 
                      if not k.startswith('_') and k != 'public' and k != 'private'}
        }
        
        # Guardamos en un file temporal
        with open("/tmp/instagram_pre_session.json", "w") as f:
            json.dump(session_data, f, indent=2)
        print(f"   ✅ Pre-session guardada en /tmp/instagram_pre_session.json")
        return client
    
    return client

# ============================================================
# TEST FINAL
# ============================================================
def final_test(user_data):
    """Test final de funcionalidad completa"""
    print(f"\n   3. Test: @{TARGET}")
    
    if not user_data:
        return [], None
    
    try:
        # Crear client con session completa
        client = Client()
        client.sessionid = user_data.get('sessionid')
        client.mid = user_data.get('mid')
        client.tray_session_id = user_data.get('tray_session_id')
        
        if client.sessionid:
            print(f"      ✅ Session loaded: {client.sessionid[:20]}...")
        else:
            print(f"      ⚠️ Sessionid missing")
        
        # Test 1: info user
        print("      Subtest 1: User info...")
        user = client.user_info_by_username(TARGET)
        
        print(f"         ✅ User ID: {user.pk}")
        print(f"         ✅ Followers: {user.followers_count:,}")
        print(f"         ✅ Display: {user.display_name}")
        
        # Test 2: followers
        print("\n      Subtest 2: Followers...")
        followers = client.user_followers(user.pk, limit=LIMIT)
        
        print(f"         ✅ SUCCESS! Total: {len(followers)}")
        print(f"\n         Samples:")
        for i, f in enumerate(followers[:min(5, len(followers))], 1):
            print(f"            {i}. @{f.username} (ID: {f.pk})")
        
        return followers, user
        
    except Exception as e:
        print(f"   ⚠️ Error: {type(e).__name__}: {e}")
        return [], None

# ============================================================
# MAIN
# ============================================================
TARGET = "nike"
LIMIT = 10

print("="*60)
print("🚀 SMOKE TEST PROXY/SESSION - Instagram Followers")
print("="*60)

# Cargar session pre-guardada
client = load_pre_saved_session()

# Ejecutar test final
followers, user = final_test(
    client.__dict__ if hasattr(client, '__dict__') else {}
)

# Guardar resultados finales
if followers or user:
    import json
    result = {
        "target": TARGET,
        "status": "success",
        "followers_count": user.followers_count if user else None,
        "sample_followers": [
            {"username": f.username, "pk": f.pk} 
            for f in (followers or [])[:3]
        ]
    }
    
    with open("/home/ubuntu/docs_dev/smoke_test_proxmox.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ TEST COMPLETADO CON ÉXITO!")
    print(f"{'='*60}")
    print(f"Resultados: {len(followers)} followers encontrados")
    print(f"Archivo: /home/ubuntu/docs_dev/smoke_test_proxmox.json")
    
    if hasattr(client, 'close'):
        client.close()

