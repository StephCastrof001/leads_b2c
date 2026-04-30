from instagrapi import Client
from .base import profile_to_dict


def extract(client: Client, username: str, amount: int = 20) -> list[dict]:
    """Seguidores de una cuenta."""
    user = client.user_info_by_username(username)
    print(f"[INFO] @{user.username} -- {user.follower_count:,} followers total")
    raw = client.user_followers(user.pk, amount=amount)
    print(f"[INFO] Fetched {len(raw)} follower IDs")
    results = []
    for i, uid in enumerate(raw, 1):
        try:
            results.append(profile_to_dict(client, uid))
            if i % 5 == 0:
                print(f"[INFO] {i}/{len(raw)} processed")
        except Exception as e:
            print(f"[WARN] Skipped {uid}: {type(e).__name__}")
    return results
