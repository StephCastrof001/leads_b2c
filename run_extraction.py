import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from scraper.scraper import SocLeadsScraper
from models.data_models import Platform

async def main():
    print('🚀 Iniciando Scraper de Producción...')
    scraper = SocLeadsScraper(headless=True)
    
    try:
        # 1. Hacer Login
        success = await scraper.login()
        if not success:
            print('❌ FALLÓ el login. Abortando extracción.')
            return
            
        print('✅ LOGIN EXITOSO. Iniciando búsqueda de leads...')
        
        # 2. Crear y correr el Job
        job = await scraper.create_job(Platform.INSTAGRAM, 'Marketing Agencies')
        job_success = await scraper.run_scrape_job(job)
        
        if job_success:
            print(f'✅ ¡JOB COMPLETADO! Revisa los resultados para el job: {job.id}')
        else:
            print('❌ FALLÓ el job de extracción.')
            
    except Exception as e:
        print(f'💥 ERROR CRÍTICO: {e}')
    finally:
        if scraper.playwright:
            await scraper.playwright.stop()
            print('🧹 Limpieza completada.')

asyncio.run(main())
