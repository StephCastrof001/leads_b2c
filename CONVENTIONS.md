# CONVENTIONS — Python / Playwright Scraper

Guia de estilo para Aider. Aplica a todos los cambios en este repo.

## Estilo general
- Black formatter, 88 chars max
- Type hints en todas las funciones publicas: `def login(self) -> bool:`
- Snake_case variables/funciones, PascalCase clases
- f-strings sobre .format() o %
- Async/await en toda la capa de I/O — nunca requests sincronos si hay alternativa

## Estructura de clases Playwright
- Siempre inicializar en `__init__`: `self.playwright = None`, `self.browser = None`, `self.page = None`
- `async def start(self) -> None` — inicia playwright y browser
- `async def stop(self) -> None` — cierra page, browser, playwright en ese orden
- `async def login(self) -> bool` — retorna True si exitoso, False si falla
- NO usar `try/finally` en `login()` para cerrar browser — eso rompe el lifecycle si login falla

## Retry logic
- Maximos 3 intentos con backoff exponencial: `await asyncio.sleep(2 ** attempt)`
- Siempre loggear el intento: `logger.warning("retry attempt=%d error=%s", attempt, e)`
- Despues de 3 fallos: raise o retornar None/False segun el contrato de la funcion

## Logging
- Usar structlog o logging estandar con campos clave: `action`, `status`, `detail`
- Formato: `logger.info("accion completada", action="login", status="ok", user=user_id)`
- NUNCA loggear: passwords, tokens, cookies, session_ids

## Manejo de errores
- Capturar excepciones especificas, no bare `except:`
- `playwright.errors.TimeoutError` → retry
- `Exception` generica → log + re-raise o retornar None
- No silenciar errores con `except: pass`

## Selectores Playwright
- Preferir `page.locator()` sobre `page.querySelector()`
- Siempre usar `await locator.wait_for()` antes de interactuar
- Timeout explicito: `await page.wait_for_selector(".clase", timeout=10000)`

## Anti-patrones conocidos
- NO regenerar el archivo completo si el cambio es puntual (usa diff format en archivos >100 lineas)
- NO agregar dependencias nuevas sin spec explicita
- NO cambiar firmas de metodos publicos sin actualizar el CONTRACT del spec
- NO commitear cookies, tokens o credenciales en ningun archivo
