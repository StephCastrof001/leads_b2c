from instagrapi import Client
import time


def setup_instagram_session():
    client = Client()
    
    # Proxies residenciales (opcional - evita bans)
    # Para usar: client.set_proxy("host:port@user:password")
    # Por ahora ejecutamos sin proxy para probar la autenticación
    # client.pre_login_flow(concurrency=1) # Sin proxy
    
    # Pre-autenticación (prepara las cookies y headers)
    success = client.pre_login_flow()
    if success:
        print("✅ Pre-flow exitoso")
        
        # Ahora intenta login con las credentials
        try:
            result = client.login("ValesNissanCombustible", "20063288")
            print("✅ Login exitoso!")
            print(f"Session ID: {getattr(client, 'sessionid', 'N/A')[:40]}...\n")
            return client
        except Exception as login_e:
            print(f"⚠️ Login falló: {login_e}")
            # Intento alternativo: guardar session manualmente
            print("\nIntentando guardar session para login web...")
            print("Verifica en https://app.instagram.com/challenge/?flow=web_flow_consent para sessionid")
            # Intentar acceder a attributes de session
            session_attrs = [attr for attr in dir(client) if 'session' in attr.lower()]
            print(f"Available session attrs: {session_attrs[:5]}")
            return client
    
    return client


def get_followers(client, username):
    """Obtiene seguidores de una página usando instagrapi"""
    try:
        user = client.user_info_by_username(username)
        followers = client.user_followers(user.pk)
        
        print(f"\n{'='*50}")
        print(f"SEGUIDORES DE @{username}:")
        print(f"{'='*50}")
        print(f"Usuario ID: {user.pk}")
        print(f"Display Name: {user.display_name}")
        print(f"Bio: {user.bio}")
        print(f"Followers Count: {user.followers_count}")
        print(f"Following Count: {user.following_count}")
        print(f"Posts Count: {user.media_count}")
        print(f"Is Verified: {user.is_verified}")
        print(f"Is Private: {user.is_private}")
        print(f"\nPrimeros {len(followers)} seguidores:")
        print(f"{'='*50}")
        
        for i, follower in enumerate(followers[:min(10, len(followers))]):
            print(f"{i+1}. {follower.username} (ID: {follower.pk})")
        
        if len(followers) > 10:
            print(f"\n... y {len(followers) - 10} más")
        
        print(f"\nTotal: {len(followers)} seguidores disponibles")
        print(f"{'='*50}\n")
        
        return followers, user
        
    except Exception as e:
        print(f"\n⚠️ Error al obtener seguidores de @{username}:")
        print(f"   {type(e).__name__}: {e}")
        return [], None


def main():
    # Setup de sesión
    print("🔄 Iniciando Instagram CLI interactivo...")
    print("   (Te pedirá que confirmes el login en el navegador)")
    client = setup_instagram_session()
    
    # Ejecutar scraping
    target = "nike"  # Cambia esto a la página objetivo
    print(f"📍 Iniciando scrape de @{target}...\n")
    
    followers, user = get_followers(client, target)
    
    # Guardar en archivo (opcional)
    import json
    if followers and user:
        result = {
            "username": target,
            "followers_count": user.followers_count,
            "sample_followers": [
                {"username": f.username, "pk": f.pk} 
                for f in followers[:5]
            ]
        }
        
        output_file = "/home/ubuntu/docs_dev/followers_sample.json"
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)
        print(f"💾 Sample guardado en: {output_file}")
    
    return client


if __name__ == "__main__":
    client = main()
    client.close()
