import os
import re
from firecrawl import FirecrawlApp

_app: FirecrawlApp | None = None


def _get_app() -> FirecrawlApp:
    global _app
    if _app is None:
        key = os.getenv("FIRECRAWL_API_KEY")
        if not key:
            raise SystemExit("[ERROR] Set FIRECRAWL_API_KEY in .env")
        _app = FirecrawlApp(api_key=key)
    return _app


def enrich(profiles: list[dict]) -> list[dict]:
    """Scrape cada website en bio con Firecrawl y extrae emails/phones reales."""
    app = _get_app()
    enriched = 0
    for p in profiles:
        if not p.get("website"):
            continue
        try:
            result = app.scrape_url(p["website"], params={"formats": ["markdown"]})
            text = result.get("markdown", "")
            emails = list(set(re.findall(
                r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text
            )))
            phones = list(set(re.findall(
                r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text
            )))
            p["emails_web"] = emails
            p["phones_web"] = phones
            enriched += 1
            print(f"[INFO] @{p['username']} -> {len(emails)} emails, {len(phones)} phones")
        except Exception as e:
            print(f"[WARN] Firecrawl failed for {p['website']}: {type(e).__name__}")
    print(f"[INFO] Enriched {enriched}/{len(profiles)} profiles")
    return profiles
