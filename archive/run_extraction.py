"""
RUN EXTRACTION - clinicavesaliooficial + followers
"""

from instagrapi import Client
import time
import json

print("="*60)
print("🚀 FINAL EXTRACTION - clinicavesaliooficial + Followers")
print("="*60)

client = Client()

# Step 1: Pre-flow
print("\nStep 1: Pre-flow...")
client.pre_login_flow()
print("✅ OK")
time.sleep(2)

# Step 2: Login Flow (Interactive)
print("\nStep 2: Open Browser + Login...")
print("""
1. Abre este link en navegador:
   https://www.instagram.com/accounts/login/

2. Ingresa tus credentials:
   Username: ValesNissanCombustible
   Password: 20063288

3. Al entrar al perfil, presiona F12 -> Network
   Busca el cookie "sessionid" y cópialo.
""")

# Paso 3: Configurar client con sessionid
try:
    sessionid = input("\n4. Pega el sessionid aquí: ").strip()
    client = Client()
    client.sessionid = sessionid
    client.mid = sessionid[:20]
    print(f"✅ Session loaded: {sessionid[:30]}...")
    time.sleep(2)
    
    # Step 4: Test User Info
    print(f"\nStep 3: User Info: 'clinicavesaliooficial'...")
    try:
        user = client.user_info_by_username("clinicavesaliooficial")
        print(f"✅ User: {user.username}, ID: {user.pk}")
        print(f"✅ Followers: {user.followers_count:,}")
        
        # Step 5: Get Followers
        print(f"\nStep 4: Followers (limit=10)...")
        followers = client.user_followers(user.pk, limit=10)
        print(f"✅ Total: {len(followers)}")
        
        # Show samples
        print(f"\n   Samples ({min(5, len(followers))}...")
        for i, f in enumerate(followers[:min(5, len(followers))], 1):
            print(f"      {i}. @{f.username} (ID: {f.pk})")
        
        # Step 6: Save to File
        print(f"\nStep 5: Saving files...")
        with open("followers_sample.json", "w") as f:
            json.dump({
                "target": "clinicavesaliooficial",
                "count": len(followers),
                "samples": [{"username": fl.username, "pk": fl.pk} for fl in followers[:5]]
            }, f, indent=2)
        print("✅ Saved: followers_sample.json")
        
        with open("followers_sample.csv", "w") as f:
            f.write("index,username,pk\n")
            for i, ff in enumerate(followers[:10], 1):
                f.write(f"{i},{ff.username},{ff.pk}\n")
        print("✅ Saved: followers_sample.csv")
        
    except Exception as e:
        print(f"⚠️ Error: {type(e).__name__}: {e}")
        if hasattr(client, 'last_json'):
            print(f"   Detail: {client.last_json}")
    
    print(f"\n✅ Done!")
    
except Exception as e:
    print(f"⚠️ Error: {type(e).__name__}: {e}")
finally:
    try:
        client.close()
        print("✅ Client closed")
    except:
        pass
