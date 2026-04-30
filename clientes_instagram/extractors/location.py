from instagrapi import Client
from .base import profile_to_dict


def extract(client: Client, location_id: int, amount: int = 50) -> list[dict]:
    """Usuarios unicos en posts recientes de una ubicacion.

    Para encontrar location_id: buscar la ubicacion en IG y copiar el ID de la URL.
    Ejemplo: Lima, Peru = 212988663
    """
    medias = client.location_medias_recent(location_id, amount=amount)
    print(f"[INFO] Fetched {len(medias)} recent posts for location {location_id}")
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
            print(f"[WARN] Skipped {uid}: {type(e).__name__}")
    print(f"[INFO] {len(results)} unique users at location {location_id}")
    return results
