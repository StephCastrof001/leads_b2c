"""
🚀 SCRIPT FINAL - SMOKE TEST REAL
Target: clinicavesaliooficial + Followers (limit=10)
"""

from instagrapi import Client
import time
import json
import sys

print("="*60)
print("🚀 SMOKE TEST FINAL - clinicavesaliooficial + Followers")
print("="*60)

client = Client()

# Step 1: Pre-flow
print("\nStep 1: Pre-flow...")
client.pre_login_flow()
print("✅ Pre-flow: OK")
time.sleep(2)

# Step 2: Session Real (Manual de https://www.instagram.com/challenge/)
print("\nStep 2: Configurar Session Real...")
print("""
   1. Abre: https://www.instagram.com/challenge/
   2. Ingresa tus credentials
   3. F12 -> Network -> Headers -> Cookies
   4. Copia el valor de "sessionid" (ej: "AbCdEf123456789...")
""")

# Lectura interactiva de sessionid
try:
    sessionid = input("\n   5. Pega el sessionid aquí: ").strip()
except EOFError:
    sessionid = "COPIA_SESSIONID_AQUI"

if sessionid == "COPIA_SESSIONID_AQUI":
    print(f"   ⚠️ Session: {sessionid}")
else:
    print(f"   ✅ Session: {sessionid[:30]}...")

time.sleep(2)

# Step 3: User Info
print(f"\nStep 3: User Info: 'clinicavesaliooficial'...")
try:
    user = client.user_info_by_username("clinicavesaliooficial")
    print("✅ SUCCESS!")
    print(f"   - Username: {user.username}")
    print(f"   - ID: {user.pk}")
    print(f"   - Followers: {user.followers_count:,}")
    print(f"   - Following: {user.following_count}")
    
except Exception as e:
    print(f"   ⚠️ Error (429): {type(e).__name__}")
    print("   → Pausar 3s y reintentar...")
    time.sleep(3)
    try:
        user = client.user_info_by_username("clinicavesaliooficial")
        print("✅ Retry 1: SUCCESS!")
    except:
        print("   → Retry 2...")
        time.sleep(3)
        user = client.user_info_by_username("clinicavesaliooficial")
        print("✅ Retry 2: SUCCESS!")

# Step 4: Followers
print(f"\nStep 4: Followers (limit=10)...")
try:
    followers = client.user_followers(user.pk, limit=10)
    print(f"✅ SUCCESS! Total: {len(followers)}")
    
    # Sample
    print(f"\n   Samples ({min(5, len(followers))}...")
    for i, f in enumerate(followers[:min(5, len(followers))], 1):
        print(f"      {i}. @{f.username} (ID: {f.pk})")
    
except Exception as e:
    print(f"   ⚠️ Error: {type(e).__name__}: {e}")

# Step 5: Save to File
print(f"\nStep 5: Saving files...")
try:
    with open("followers_sample.json", "w") as f:
        json.dump({
            "target": "clinicavesaliooficial",
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "count": len(followers) if user else 0,
            "samples": [{"username": fl.username, "pk": fl.pk} for fl in followers[:5]]
        }, f, indent=2)
    print("✅ Saved: followers_sample.json")
    
    with open("followers_sample.csv", "w") as f:
        f.write("index,username,pk\n")
        for i, ff in enumerate(followers[:10], 1):
            f.write(f"{i},{ff.username},{ff.pk}\n")
    print("✅ Saved: followers_sample.csv")
    
except Exception as e:
    print(f"   ⚠️ Error: {e}")

# Step 6: Show Full Result
print(f"\n{'='*60}")
print("📊 EXTRACTION RESULT - clinicavesaliooficial")
print(f"{'='*60}")
print(f"   ✅ User:      {user.username if user else 'unknown'}")
print(f"   ✅ ID:        {user.pk if user else 'unknown'}")
print(f"   ✅ Followers: {user.followers_count if user else 'unknown'}")
print(f"   ✅ Samples:   {len(followers) if user else 0}")
print(f"   ✅ Time:      {time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"   ✅ Files:     followers_sample.json, followers_sample.csv")
print(f"{'='*60}")

client.close()
input("\n✅ Press ENTER to exit...")
