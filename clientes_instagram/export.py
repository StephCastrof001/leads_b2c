import csv
import json
from pathlib import Path


def save_json(data: dict, path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[INFO] Saved JSON: {path}")


def save_csv(profiles: list[dict], path: Path) -> None:
    if not profiles:
        print("[WARN] No profiles to export")
        return
    fields = [
        "username", "full_name", "bio", "website", "followers",
        "is_business", "emails_in_bio", "phones_in_bio",
        "emails_web", "phones_web",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for p in profiles:
            row = {**p}
            row["emails_in_bio"] = "; ".join(p.get("emails_in_bio", []))
            row["phones_in_bio"] = "; ".join(p.get("phones_in_bio", []))
            row["emails_web"]    = "; ".join(p.get("emails_web", []))
            row["phones_web"]    = "; ".join(p.get("phones_web", []))
            writer.writerow(row)
    print(f"[INFO] Saved CSV: {path} ({len(profiles)} rows)")
