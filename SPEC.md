
Implementa un scraper de SocLeads (app.socleads.com) en dos fases.
Lee el .env para todas las credenciales y configuracion.

=== FASE 1: recon/recon.py — API Mapper (0 creditos, solo recon) ===

Usa Playwright (async) para:
1. Login en SOCLEADS_BASE_URL con SOCLEADS_EMAIL/PASSWORD
2. Interceptar TODOS los requests de red (page.on request+response)
3. Navegar manualmente cada seccion del dashboard:
   - /dashboard, /scraper, /history, /account, /billing
4. Para cada request interceptado que sea API (/api/, /v1/, fetch, XHR):
   - Guardar en API_MAP_DIR/endpoints.json: {method, url, headers, body, response_status, response_preview}
5. Tomar screenshot de cada seccion en SCREENSHOTS_DIR/
6. Al final imprimir tabla de endpoints encontrados

Reglas:
- headless=True (EC2 sin display)
- user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120"
- Timeout 30s por navegacion
- NO consumir creditos — solo navegar e interceptar

=== FASE 2: scraper/scraper.py — Scraper estrategico ===

Usa Playwright (async) + los endpoints descubiertos en Fase 1.

Plataformas habilitadas (leer ENABLED_PLATFORMS del .env):
- ig_keyword: Instagram por keyword/hashtag
- fb_keyword: Facebook por keyword  
- tiktok_keyword: TikTok por keyword
- NUNCA: google_maps, ig_followers (cobran por fila sin email)

Logica:
1. Login en SocLeads
2. Para cada platform en ENABLED_PLATFORMS:
   - Para cada keyword en KEYWORDS:
     - Iniciar scrape con esa keyword
     - Esperar resultados (polling cada 5s, max 120s)
     - Descargar resultados cuando status=completed
     - Si credits_used >= MAX_CREDITS: PARAR inmediatamente
3. Guardar todo en OUTPUT_DIR/leads_{timestamp}.json

=== scraper/models.py — Tipos de datos ===

Dataclasses para:
- Lead: platform, keyword, email, name, link, phone(optional), scraped_at
- ScrapeJob: id, platform, keyword, status, credits_used, leads: list[Lead]
- ScrapeResult: jobs: list[ScrapeJob], total_credits_used, timestamp

Reglas generales:
- Python 3.12, async/await, Playwright async
- dotenv para leer .env
- Logging estructurado: [TIMESTAMP] [LEVEL] [MODULE] mensaje
- Guardar JSON con json.dumps(indent=2)
- NO hardcodear credenciales
- Manejo de errores con retry x2 en network errors
