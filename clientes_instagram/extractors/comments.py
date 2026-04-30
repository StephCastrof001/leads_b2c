from instagrapi import Client
from .base import profile_to_dict


def extract(client: Client, media_url: str, amount: int = 50) -> list[dict]:
    """Usuarios unicos que comentaron en un post."""
    media_pk = client.media_pk_from_url(media_url)
    raw_comments = client.media_comments(media_pk, amount=amount)
    print(f"[INFO] Fetched {len(raw_comments)} comments from post")
    seen: set[str] = set()
    results = []
    for comment in raw_comments:
        uid = str(comment.user.pk)
        if uid in seen:
            continue
        seen.add(uid)
        try:
            results.append(profile_to_dict(client, uid, sleep=0.3))
        except Exception as e:
            print(f"[WARN] Skipped {uid}: {type(e).__name__}")
    print(f"[INFO] {len(results)} unique commenters")
    return results
