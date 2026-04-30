import os
from pathlib import Path
from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

load_dotenv()
SESSION_FILE = Path(__file__).parent / "session.json"


def get_client() -> Client:
    cl = Client()
    if proxy := os.getenv("PROXY_URL"):
        cl.set_proxy(proxy)

    if SESSION_FILE.exists():
        print("[INFO] Loading session...")
        cl.load_settings(SESSION_FILE)
        try:
            cl.get_timeline_feed()
            print("[INFO] Session valid")
            return cl
        except LoginRequired:
            print("[WARN] Session expired, re-authenticating")
            SESSION_FILE.unlink(missing_ok=True)

    if sid := os.getenv("IG_SESSION_ID"):
        print("[INFO] Login via sessionid...")
        cl.login_by_sessionid(sid)
        cl.dump_settings(SESSION_FILE)
        return cl

    usr, pwd = os.getenv("IG_USERNAME"), os.getenv("IG_PASSWORD")
    if not usr or not pwd:
        raise SystemExit("[ERROR] Set IG_SESSION_ID or IG_USERNAME+IG_PASSWORD in .env")
    print(f"[INFO] Login as {usr}...")
    cl.login(usr, pwd)
    cl.dump_settings(SESSION_FILE)
    return cl
