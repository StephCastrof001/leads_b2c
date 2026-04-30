from instagrapi import Client
from .base import profile_to_dict


def extract(client: Client, tag: str, amount: int = 50) -> list[dict]:
    "Usuarios unicos en posts recientes de un hashtag."
    tag = tag.lstrip(#)
    medias = client.hashtag_medias_recent(tag, amount=amount)
    print(f[INFO] Fetched {len(medias)} recent posts for #{tag})
    seen: set[str] = set()
    results = []
    for media in medias:
        uid = str(media.user.pk)
        if uid in seen:
            continue
        seen.add(uid)
        try:
            results.append(profile_to_dict(client, uid, sleep=0.3))
        except Exception as e:
            print(f[WARN] Skipped {uid}: {type(e).__name__})
    print(f[INFO] {len(results)} unique users from #{tag})
    return results
