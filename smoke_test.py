import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))
from scraper.scraper import SocLeadsScraper

async def test_login():
    print('Iniciando Smoke Test Final (Stealth Mode)...')
    scraper = SocLeadsScraper(headless=True)
    try:
        success = await scraper.login()
        if success:
            print('LOGIN EXITOSO: Cloudflare evadido y login completado! (True)')
        else:
            print('FALLO: El scraper no pudo hacer login.')
    except Exception as e:
        print(f'ERROR CRITICO: {e}')
    finally:
        if scraper.playwright:
            await scraper.playwright.stop()
            print('Limpieza completada.')

asyncio.run(test_login())
