# CLAUDE.md â€” Pulse IA
> Instrucciones locales del proyecto. Tienen prioridad sobre reglas globales.

## Proyecto
Pulse IA â€” Fabrica de leads B2B para LatAm.
Directorio: D:/Pulse-ia
Stack: Vite + React (frontend), FastAPI Python (backend), PocketBase (DB), Apify (scraping), Yape (pagos)

---

## Reglas Firecrawl (OBLIGATORIO)

Antes de usar cualquier tool de Firecrawl (firecrawl_search, firecrawl_scrape, firecrawl_agent):
1. CONSULTAR al usuario si aprueba el uso y cuantos creditos gastara
2. MOSTRAR el output raw completo al usuario sin procesar
3. GUARDAR el log en D:/Pulse-ia/firecrawl_logs/NNN_nombre_descriptivo.json con este formato:
   {
     timestamp: ...,
     tool: firecrawl_search|firecrawl_scrape|firecrawl_agent,
     credits_used: N,
     input: { ...parametros exactos usados... },
     output: { ...respuesta raw completa... },
     notes: observacion del resultado
   }
4. Nombrar archivos secuencialmente: 001_, 002_, 003_...
5. NUNCA lanzar agentes con acceso a Firecrawl sin advertir el costo estimado

Razon: el usuario pago creditos de Firecrawl y necesita control total del gasto.

---

## Reglas Apify

- Siempre probar manualmente en Apify Console antes de codificar
- Maximo 50-100 resultados en pruebas, escalar solo si el test funciona
- Guardar datasets descargados en: D:/Pulse-ia/pruebas_apify_manual/

---

## Estructura de carpetas

D:/Pulse-ia/
  src/                  <- Frontend React (Vite)
  backend/              <- FastAPI Python (pendiente)
  scraping/             <- JSONs de prueba Apify
  pruebas_apify_manual/ <- Datasets manuales + documentacion
  firecrawl_logs/       <- Logs de cada busqueda Firecrawl
  shared/               <- Tipos compartidos

---

## Pagos
Solo Yape. PayPal y Culqi fueron eliminados del scope.

---

## Nichos B2B validados
Ver: D:/Pulse-ia/pruebas_apify_manual/nichos_b2b_investigacion.md
Pipeline principal: Google Maps scraper -> CSV con telefono + email
Zona piloto: Las Malvinas + La Bellota + Plaza Ferretero (Lima)

---

## Scraping Multi-Sitio â€” Reglas (aprendidas en sesiÃ³n 2026-03-24)

### ANTES de scrapear cualquier sitio nuevo
1. Leer `D:/Pulse-ia/docs_dev/task_plan.md` â€” si no existe, CREARLO primero
2. Definir herramienta correcta segÃºn tipo de sitio (ver tabla abajo)
3. DiseÃ±ar schema unificado objetivo ANTES de empezar
4. Crear entrada en task_plan.md con fases y decisiones

### DURANTE el scraping
- **2-action rule:** cada 2 scrapes completados â†’ STOP â†’ actualizar `docs_dev/findings.md`
- **Marcar fases en tiempo real:** completar [x] en task_plan.md al terminar cada fase
- **Raw first:** guardar JSON nativo del sitio SIN normalizar â†’ homologar en paso separado
- **3-strikes:** si algo falla 3 veces â†’ escalar al usuario con intentos documentados

### Herramienta por tipo de sitio
| Tipo | Sitio ejemplo | Tool | Razon |
|---|---|---|---|
| SSR simple | cuidafarma.pe (Saleor) | Firecrawl basic | Sin antibot |
| SSR + antibot | falabella.com.pe (Next.js + Akamai) | Firecrawl stealth | Requiere proxy |
| SPA Angular/Vue | inkafarma.pe | Playwright | Precios JS dinamicos |
| Google SERP | cualquier busqueda | ScrapingBee | Especializado y barato |

### Estructura de archivos scraping
```
scraping/schemas/{sitio}_schema.md   <- schema nativo por sitio
scraping/scripts/{sitio}_*.cjs       <- scripts Playwright (.cjs por type:module)
scraping/output/{sitio}_{sku}_raw.json  <- output raw SIN normalizar
docs_dev/task_plan.md                <- plan + fases + decisiones
docs_dev/findings.md                 <- hallazgos por sesion
docs_dev/progress.md                 <- log de sesion
tasks/lessons.md                     <- lecciones tecnicas del proyecto
```

### Errores conocidos en este proyecto
- `waitUntil: networkidle` â†’ timeout en SPAs â†’ usar `waitUntil: load`
- `.js` con `require()` â†’ error en proyecto con `type: module` â†’ usar `.cjs`
- Write tool bloqueado por hook (espacios en path) â†’ usar Bash heredoc
- `__NEXT_DATA__` de Falabella â†’ field names NO son normalPrice/cmrPrice â†’ pendiente mapear

### Sitios ya mapeados (schemas listos)
- cuidafarma.pe â†’ `scraping/schemas/cuidafarma_schema.md`
- inkafarma.pe  â†’ `scraping/schemas/inkafarma_schema.md`
- falabella.com.pe â†’ `scraping/schemas/falabella_schema.md`

## Skill routing

When the user's request matches an available skill, ALWAYS invoke it using the Skill
tool as your FIRST action. Do NOT answer directly, do NOT use other tools first.
The skill has specialized workflows that produce better results than ad-hoc answers.

Key routing rules:
- Product ideas, is this worth building, brainstorming â†’ invoke office-hours
- Bugs, errors, why is this broken, 500 errors â†’ invoke investigate
- Ship, deploy, push, create PR â†’ invoke ship
- QA, test the site, find bugs â†’ invoke qa
- Code review, check my diff â†’ invoke review
- Update docs after shipping â†’ invoke document-release
- Weekly retro â†’ invoke retro
- Design system, brand â†’ invoke design-consultation
- Visual audit, design polish â†’ invoke design-review
- Architecture review â†’ invoke plan-eng-review

