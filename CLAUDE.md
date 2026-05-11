# SocLeads Scraper

## Stack
- Python 3.11 + Playwright async API
- Plataformas activas: ig_keyword, fb_keyword, tiktok_keyword (UNICOS permitidos)
- MAX_CREDITS: 100 — guard en scraper.py

## Archivos clave
- scraper/scraper.py (318 lineas) → usar --edit-format diff siempre
- scraper/models.py → dataclasses Lead, ScrapeJob, Platform enum
- recon/recon.py → API mapper Playwright (0 creditos)

## Comandos
- Runner: nohup ~/task-runner.sh > /tmp/runner.log 2>&1 &
- Ver log: tail -f /tmp/aider_NNN_nombre.log
- Push: git push origin feat/socleads

## PR activo
- feat/socleads → PR 8 en leads_b2c
- Pendientes: 003 Playwright lifecycle, 004 credentials guard, 005 TimeoutError split
