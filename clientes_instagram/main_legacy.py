import os
import json
import time
import re
from pathlib import Path
from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

load_dotenv()

SESSION_FILE    = Path(__file__).parent / "session.json"
OUTPUT_DIR      = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

TARGET          = os.getenv("IG_TARGET", "clinicavesaliooficial")
FOLLOWERS_LIMIT = int(os.getenv("IG_FOLLOWERS_LIMIT", "20"))
SLEEP_BETWEEN   = float(os.getenv("IG_SLEEP_BETWEEN", "0.5"))


def get_client() -> Client:
    client = Client()
    proxy = os.getenv("PROXY_URL")
    if proxy:
        client.set_proxy(proxy)

    # 1. Sesion guardada en disco (sin request de login)
    if SESSION_FILE.exists():
        print("[INFO] Loading saved session...")
        client.load_settings(SESSION_FILE)
        try:
            client.get_timeline_feed()
            print("[INFO] Session valid")
            return client
        except LoginRequired:
            print("[WARN] Session expired")
            SESSION_FILE.unlink(missing_ok=True)

    # 2. sessionid del browser (funciona desde EC2 sin proxy)
    sessionid = os.getenv("IG_SESSION_ID")
    if sessionid:
        print("[INFO] Logging in via browser sessionid...")
        client.login_by_sessionid(sessionid)
        client.dump_settings(SESSION_FILE)
        print("[INFO] Session cached to session.json")
        return client

    # 3. user/pass (puede fallar desde datacenter IPs)
    username = os.getenv("IG_USERNAME")
    password = os.getenv("IG_PASSWORD")
    if not username or not password:
        raise SystemExit("[ERROR] Set IG_SESSION_ID or IG_USERNAME+IG_PASSWORD in .env")
    print(f"[INFO] Logging in as {username}...")
    client.login(username, password)
    client.dump_settings(SESSION_FILE)
    print("[INFO] Session cached to session.json")
    return client


def _extract_emails(text: str) -> list:
    return re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text or "")


def _extract_phones(text: str) -> list:
    return re.findall(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text or "")


def main():
    print("=" * 60)
    print("Instagram Follower Extractor - EC2 Autonomous")
    print("=" * 60)

    client = get_client()

    print("[INFO] Target: @" + TARGET)
    user = client.user_info_by_username(TARGET)
    print(f"[INFO] {user.username} - {user.follower_count:,} followers total")

    print(f"[INFO] Fetching {FOLLOWERS_LIMIT} followers...")
    followers_dict = client.user_followers(user.pk, amount=FOLLOWERS_LIMIT)
    followers = list(followers_dict.values())
    print(f"[INFO] Got {len(followers)} followers")

    results = []
    for i, f in enumerate(followers, 1):
        time.sleep(SLEEP_BETWEEN)
        try:
            info = client.user_info(f.pk)
            results.append({
                "username":      info.username,
                "pk":            info.pk,
                "full_name":     info.full_name,
                "bio":           info.biography,
                "website":       str(info.external_url) if info.external_url else None,
                "followers":     info.follower_count,
                "is_business":   info.is_business,
                "emails_in_bio": _extract_emails(info.biography),
                "phones_in_bio": _extract_phones(info.biography),
            })
            if i % 5 == 0:
                print(f"[INFO] {i}/{len(followers)} processed")
        except Exception as e:
            print(f"[WARN] Skipped @{f.username}: {type(e).__name__}")

    output = {
        "target":                 TARGET,
        "target_followers_total": user.follower_count,
        "extracted_at":           time.strftime("%Y-%m-%dT%H:%M:%S"),
        "sample_count":           len(results),
        "followers":              results,
    }

    out_file = OUTPUT_DIR / f"{TARGET}_followers.json"
    with open(out_file, "w", encoding="utf-8") as fh:
        json.dump(output, fh, indent=2, ensure_ascii=False)

    with_email = sum(1 for r in results if r["emails_in_bio"])
    with_phone = sum(1 for r in results if r["phones_in_bio"])
    print("[INFO] Saved: " + str(out_file))
    print(f"[INFO] {len(results)} followers | {with_email} with email | {with_phone} with phone")



if __name__ == "__main__":
    main()
