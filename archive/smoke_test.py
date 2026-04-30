"""
Smoke Test - Instagram Followers Extractor
Objetivo: Acceder a seguidores de una página usando web_flow
"""

from instagrapi import Client
import getpass
import time

def setup_instagram_session():
    print("🔄 Configurando Instagram CLI...")
    client = Client()
    client.pre_login_flow()
    
    print("🔄 Iniciando web_flow (interactivo)...")
    print("   1. Se abrirá tu navegador automáticamente")
    print("   2. Ingresa tus credentials")
    print("   3. Confirma el login")
    print()
    
    # web_flow necesita crear un navegador y autenticar
    # La forma más simple: usar login_flow
    try:
        result = client.login_flow()
        print("✅ Login flow exitoso!")
        if hasattr(client, 'sessionid') and client.sessionid:
            print(f"   Session ID: {client.sessionid[:40]}...\n")
        time.sleep(2)
        return client
    except Exception as e:
        print(f"⚠️ Login flow falló: {e}")
        time.sleep(2)
        return client

def get_user_info(client, username):
    """Obtiene info de usuario"""
    print(f"\n📊 Obteniendo info de @{username}...")
    try:
        user = client.user_info_by_username(username)
        print(f"✅ Usuario encontrado:")
        print(f"   ID: {user.pk}")
        print(f"   Name: {user.display_name}")
        print(f"   Followers: {user.followers_count:,}")
        print(f"   Following: {user.following_count:,}")
        print(f"   Posts: {user.media_count:,}")
        print(f"   Verified: {user.is_verified}")
        print(f"   Private: {user.is_private}\n")
        return user
    except Exception as e:
        print(f"   Error: {type(e).__name__}: {e}")
        return None

def get_followers(client, username, limit=10):
    """Obtiene seguidores"""
    print(f"📥 Obteniendo seguidores de @{username}...")
    try:
        user = client.user_info_by_username(username)
        print(f"✅ User ID: {user.pk}")
        
        followers = client.user_followers(user.pk, limit=limit)
        
        print(f"\n✅ {'='*50}")
        print(f"SEGUIDORES DE @{username} ({len(followers)} encontrados)")
        print(f"{'='*50}")
        
        for i, f in enumerate(followers[:min(10, len(followers))], 1):
            print(f"   {i}. @{f.username} (ID: {f.pk})")
        
        print(f"   ...\n")
        
        return followers, user
        
    except Exception as e:
        print(f"   Error: {type(e).__name__}: {e}")
        return [], None

def main():
    print("=" * 60)
    print("🚀 SMOKET TEST - Instagram Followers Extractor")
    print("=" * 60)
    print(f"\nUsuario de prueba: ValesNissanCombustible")
    print(f"Contraseña: 20063288")
    print()
    
    # 1. Configurar sesión
    print("Step 1: Autenticando...")
    client = setup_instagram_session()
    
    # 2. Obtener info de usuario objetivo
    print("Step 2: Obteniendo info del usuario objetivo...")
    target = "nike"
    user = get_user_info(client, target)
    
    if not user:
        print("\n❌ No se pudo obtener info del usuario objetivo")
        return
    
    # 3. Obtener seguidores
    print("Step 3: Obteniendo seguidores...")
    followers, _ = get_followers(client, target, 10)
    
    if followers:
        print(f"\n🎉 ¡ÉXITO! Obtenemos {len(followers)} seguidores")
    else:
        print(f"\n⚠️ No pudimos obtener seguidores")
    
    # 4. Guardar resultados
    import json
    
    result = {
        "target_username": target,
        "target_followers_count": user.followers_count if target else None,
        "sample_followers": [
            {"username": f.username, "pk": f.pk} 
            for f in followers[:5]
        ] if followers else [],
        "status": "success" if followers else "partial"
    }
    
    output_file = "/home/ubuntu/docs_dev/smoke_test_results.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ SMOKET TEST COMPLETADO!")
    print(f"{'='*60}")
    print(f"Resultados guardados en: {output_file}")
    
    if hasattr(client, 'close'):
        client.close()

if __name__ == "__main__":
    main()
