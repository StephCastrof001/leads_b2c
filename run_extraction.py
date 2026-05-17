import asyncio
import os
import sys

from scraper.models import Platform, ScrapeJob
from scraper.scraper import SocLeadsScraper

async def main():
    print("🚀 Iniciando Scraper de Produccion...")
    scraper = SocLeadsScraper()
    job = ScrapeJob(id="test_001", keyword="Marketing Agencies", platform=Platform.IG_KEYWORD)
    try:
        results = await scraper.run_scrape_job(job)
        if results:
            print(f"✄ EXTRACCION FINALIZADA: {len(results.leads)} leads encontrados.")
        else:
            print("❌ FALLÓ el job de extracción.")
    except Exception as e:
        print(f"💨 ERROR CRÍTICO: {e}")
    finally:
        print("🙹🏼 Limpieza completada.")

if __name__ == "__main__":
    asyncio.run(main())
