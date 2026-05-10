# Task: Dataset de Productos mas Vendidos por Sector - Peru

## Objetivo
Construir dataset CSV/JSON de productos ecommerce Peru con precios completos
para scoring manual de productos mas vendidos por sector.

## Sectores objetivo
1. Dermocosmetica / Antiacne (ACTIVO)
2. Herramientas Electricas (ACTIVO - scrapingbee hecho)
3. [siguiente sector por definir]

## Fases

### SECTOR: Dermocosmetica
- [x] Phase 1: Schema discovery cuidafarma.pe (Saleor)
- [x] Phase 2: Schema discovery inkafarma.pe (Angular + Playwright)
- [x] Phase 3: Schema discovery falabella.com.pe (Next.js + stealth)
- [ ] Phase 4: Extraccion masiva categoria antiacne (3 sitios â†’ CSV)
- [ ] Phase 5: Scoring y analisis manual

### SECTOR: Herramientas Electricas
- [x] Phase 1: Google SERP via ScrapingBee â†’ 9 dominios identificados
- [ ] Phase 2: Decision A/B/C (ver abajo)
- [ ] Phase 3: Schema discovery top retailers
- [ ] Phase 4: Extraccion masiva â†’ CSV
- [ ] Phase 5: Scoring y analisis

## Decision Pendiente: Herramientas Electricas

| Opcion | Descripcion | Pros | Contras |
|---|---|---|---|
| A | Scrapear promart + sodimac + falabella | Dataset rapido, precios reales | 3 schemas nuevos |
| B | Mas keywords Google (taladro, amoladora) | Mapa completo del mercado | Solo SERP, no precios |
| C | Analizar cahema.pe + ayl.pe como leads B2B | Directo al core de Pulse IA | Cambia el objetivo |

**Recomendacion CTO:** A primero (datos reales), luego C si los distribuidores aparecen interesantes.

## Decisiones Tomadas

| Decision | Razon | Fecha |
|---|---|---|
| Usar Playwright para inkafarma | Angular SPA â€” precios Oh! son JS dinamico | 2026-03-24 |
| Usar Firecrawl stealth para falabella | SSR + anti-bot Akamai | 2026-03-24 |
| Firecrawl basic para cuidafarma | Saleor sin anti-bot | 2026-03-24 |
| ScrapingBee para Google SERP | Mas barato que Firecrawl para busquedas | 2026-03-24 |

## Errores Encontrados

| Error | Intento | Resolucion |
|---|---|---|
| networkidle timeout inkafarma | waitUntil networkidle | Cambiar a waitUntil: load |
| require() en ES module | .js en proyecto con type:module | Renombrar a .cjs |
| Playwright no instalado | require('playwright') | npm install playwright |
| Write tool bloqueado por hook | Espacios en path C:\Users\HP SUPPORT | Usar Bash heredoc |
| __NEXT_DATA__ field names erroneos | normalPrice/cmrPrice | PENDIENTE: mapear arbol real |

