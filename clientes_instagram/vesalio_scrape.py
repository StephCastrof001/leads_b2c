#!/usr/bin/env python3
"""
Scraper rapido de followers para clinicavesaliooficial.
Extrae emails/websites del bio. Usa session.json existente.
"""
import json
import time
import re
import sys
from pathlib import Path

try:
    from instagrapi import Client
except ImportError:
    print("ERROR: pip install instagrapi")
    sys.exit(1)

SESSION_FILE = Path(__file__).parent / "session.json"
OUTPUT_FILE = Path(__file__).parent / "output" / "vesalio_full.json"
TARGET_USER = "clinicavesaliooficial"
MAX_FOLLOWERS = 500  # safe limit para no ban

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(?:\+?\d[\d\s\-\(\)]{7,}\d)")
URL_RE = re.compile(r"https?://\S+|www\.\S+")


def extract_contact(bio: str, website: str) -> dict:
    emails = EMAIL_RE.findall(bio) if bio else []
    phones = PHONE_RE.findall(bio) if bio else []
    urls = URL_RE.findall(bio) if bio else []
    if website:
        urls.insert(0, website)
    return {"emails": list(set(emails)), "phones": list(set(phones)), "websites": list(set(urls))}


def main():
    cl = Client()
    cl.load_settings(SESSION_FILE)

    try:
        cl.get_timeline_feed()
        print("[OK] Session valida")
    except Exception as e:
        print(f"[FAIL] Session invalida: {e}")
        sys.exit(1)

    print(f"[*] Buscando usuario {TARGET_USER}...")
    user = cl.user_info_by_username(TARGET_USER)
    print(f"[*] {user.username} — {user.follower_count} followers")

    print(f"[*] Extrayendo hasta {MAX_FOLLOWERS} followers...")
    followers = cl.user_followers(user.pk, amount=MAX_FOLLOWERS)
    print(f"[*] {len(followers)} followers obtenidos, enriqueciendo...")

    results = []
    enriched = 0

    for i, (pk, basic) in enumerate(followers.items(), 1):
        try:
            info = cl.user_info(pk)
            contact = extract_contact(info.biography, str(info.external_url or ""))
            record = {
                "pk": str(pk),
                "username": info.username,
                "full_name": info.full_name,
                "biography": info.biography,
                "followers": info.follower_count,
                "following": info.following_count,
                "is_business": info.is_business,
                "is_private": info.is_private,
                "is_verified": info.is_verified,
                "website": str(info.external_url or ""),
                "emails": contact["emails"],
                "phones": contact["phones"],
                "websites": contact["websites"],
                "category": info.category,
                "city": info.city_name,
            }
            results.append(record)
            if contact["emails"]:
                enriched += 1
                print(f"  [{i}/{MAX_FOLLOWERS}] @{info.username} → EMAIL: {contact['emails']}")
            elif i % 50 == 0:
                print(f"  [{i}/{MAX_FOLLOWERS}] procesados, {enriched} con email")

            time.sleep(0.8)

        except Exception as e:
            print(f"  [SKIP] pk={pk}: {e}")
            time.sleep(2)
            continue

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n=== RESULTADO ===")
    print(f"Total analizados: {len(results)}")
    print(f"Con email: {enriched} ({enriched/len(results)*100:.1f}%)")
    print(f"Guardado en: {OUTPUT_FILE}")

    emails_all = [r for r in results if r["emails"]]
    if emails_all:
        print("\nEmails encontrados:")
        for r in emails_all:
            print(f"  @{r['username']}: {r['emails']}")


if __name__ == "__main__":
    main()
