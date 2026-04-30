import re
import time
from instagrapi import Client


def _extract_emails(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text or "")


def _extract_phones(text: str) -> list[str]:
    return re.findall(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text or "")


def profile_to_dict(client: Client, user_pk: int | str, sleep: float = 0.5) -> dict:
    time.sleep(sleep)
    info = client.user_info(user_pk)
    bio = info.biography or ""
    return {
        "username":      info.username,
        "pk":            str(info.pk),
        "full_name":     info.full_name,
        "bio":           bio,
        "website":       str(info.external_url) if info.external_url else None,
        "followers":     info.follower_count,
        "is_business":   info.is_business,
        "emails_in_bio": _extract_emails(bio),
        "phones_in_bio": _extract_phones(bio),
        "emails_web":    [],
        "phones_web":    [],
    }
