"""
Instagram Lead Extractor -- CLI

Uso:
 python3 main.py followers clinicavesaliooficial --amount 50
 python3 main.py following nike --amount 20 --csv
 python3 main.py comments https://www.instagram.com/p/ABC123/ --amount 100
 python3 main.py hashtag dentistaperu --amount 50 --enrich
 python3 main.py location 212988663 --amount 50 --csv
"""
import os
import time
import argparse
from pathlib import Path
from dotenv import load_dotenv

from auth import get_client
from extractors import followers, following, comments, hashtag, location
from enricher import enrich
from export import save_json, save_csv

load_dotenv()
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

MODES = {
    "followers": "Seguidores de una cuenta",
    "following": "Cuentas que sigue una cuenta",
    "comments":  "Comentaristas de un post",
    "hashtag":   "Usuarios de un hashtag",
    "location":  "Usuarios de una ubicacion",
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Instagram Lead Extractor -- 5 modos de extraccion"
    )
    parser.add_argument("mode", choices=list(MODES.keys()))
    parser.add_argument("target", help="@username | post_url | hashtag | location_id")
    parser.add_argument("--amount", type=int, default=int(os.getenv("IG_AMOUNT", "20")))
    parser.add_argument("--enrich", action="store_true", help="Enriquecer con Firecrawl")
    parser.add_argument("--csv",    action="store_true", help="Exportar CSV ademas de JSON")
    args = parser.parse_args()

    print("=" * 60)
    print(f"Modo : {args.mode} -- {MODES[args.mode]}")
    print(f"Target : {args.target} Amount: {args.amount}")
    print("=" * 60)

    client = get_client()
    target = args.target.lstrip("@#")
    ts = time.strftime("%Y%m%dT%H%M%S")

    if args.mode == "followers":
        profiles = followers.extract(client, target, args.amount)
        stem = f"{target}_followers_{ts}"
    elif args.mode == "following":
        profiles = following.extract(client, target, args.amount)
        stem = f"{target}_following_{ts}"
    elif args.mode == "comments":
        profiles = comments.extract(client, args.target, args.amount)
        stem = f"comments_{ts}"
    elif args.mode == "hashtag":
        profiles = hashtag.extract(client, target, args.amount)
        stem = f"hashtag_{target}_{ts}"
    else:
        profiles = location.extract(client, int(target), args.amount)
        stem = f"location_{target}_{ts}"

    if args.enrich:
        profiles = enrich(profiles)

    with_contact = sum(
        1 for p in profiles
        if p.get("emails_in_bio") or p.get("emails_web") or p.get("phones_in_bio") or p.get("phones_web")
    )
    print(f"[INFO] {len(profiles)} profiles | {with_contact} with contact info")

    payload = {
        "mode":         args.mode,
        "target":       args.target,
        "extracted_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "count":        len(profiles),
        "profiles":     profiles,
    }
    save_json(payload, OUTPUT_DIR / f"{stem}.json")
    if args.csv:
        save_csv(profiles, OUTPUT_DIR / f"{stem}.csv")


if __name__ == "__main__":
    main()
