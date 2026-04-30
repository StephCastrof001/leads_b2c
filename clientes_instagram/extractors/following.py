from instagrapi import Client
from .base import profile_to_dict


def extract(client: Client, username: str, amount: int = 20) -> list[dict]:
    """Cuentas que sigue una cuenta (Premium: cuentas que sigue tu target)."""
    user = client.user_info_by_username(username)
    print(f"[INFO] @{user.username} -- {user.following_count:,} following total")
    raw = client.user_following(user.pk, amount=amount)
    print(f"[INFO] Fetched {len(raw)} following IDs")
    results = []
    for i, uid in enumerate(raw, 1):
        try:
            results.append(profile_to_dict(client, uid))
            if i % 5 == 0:
                print(f"[INFO] {i}/{len(raw)} processed")
        except Exception as e:
            print(f"[WARN] Skipped {uid}: {type(e).__name__}")
    return results
