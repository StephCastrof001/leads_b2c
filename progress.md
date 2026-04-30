# Progress Log

## Session 2026-04-20

### Acciones Realizadas
1. ✅ Investigó landscape de herramientas de lead generation
2. ✅ Analizó APIs oficiales de Meta (Instagram Graph API, Facebook Graph API)
3. ✅ Documentó técnicas que usan las empresas
4. ✅ Creó archivos de planificación en docs_dev/
5. ✅ Investigórepo sickn33/antigravity-awesome-skills (1,431+ skills)
6. ✅ Investigó técnica alternativas a APIs oficiales

### Hallazgos Clave
- Las APIs oficiales NO proporcionan emails/teléfonos
- Todas las herramientas usan web scraping + enrichment
- Proxies residenciales son críticos para evitar bans
- Instagram/Facebook tienen anti-scraping muy agresivo
- **Firecrawl NO puede hacer scraping de redes sociales** (restringido intencionalmente)
- **Instagram Private API** (no oficial) sí funciona:
  - Endpoint público: `https://i.instagram.com/api/v1/users/web_profile_info/?username=x`
  - Libraries: instagrapi, insta-wizard
- **Técnicas funcionales**:
  1. Private API (no oficial)
  2. Pattern mining en bio/website
  3. Cross-referencing con otras fuentes
  4. Playwright con anti-detección (proxies residenciales)

### Skills Identificados
- browser-automation (Playwright/Puppeteer) - Ya disponible
- senior-backend
- n8n-workflow-patterns
- senior-frontend
- planning
- Skills del repo antigravity: scraping, research, data-extraction

### Siguiente
- Implementar scraper con Firecrawl + técnica patrón mining
- Explorar skills del repo antigravity

## Errores
Ninguno documentado aún

## Decisions Pendientes
- Elegir lenguaje de backend (Node.js vs Python) - sugerencia: Python por instagrapi
- Seleccionar proveedor de proxies (Smartproxy vs Bright Data)
- Definir estrategia de anti-detección


## Session 2026-04-27

### Acciones Realizadas
1. [x] Diagnostico real de docs_dev via SSH (llave correcta: Ollama.pem en D:\Openclaw\Clave-Ollama\)
2. [x] Archivados 19 scripts legacy de smoke test a docs_dev/archive/
3. [x] Refactor completo de clientes_instagram a arquitectura modular:
       - auth.py: sesion 3-tier extraida a modulo propio
       - extractors/: 5 modulos (followers, following, comments, hashtag, location)
       - enricher.py: Firecrawl para emails reales desde websites en bio
       - export.py: JSON + CSV unificado
       - main.py: CLI con flags --enrich y --csv
4. [x] Push a GitHub via MCP (evitando problema de quotes en SSH heredoc)
       URL: https://github.com/StephCastrof001/clientes_extracciondatos
5. [x] task_plan.md actualizado con arquitectura basada en benchmark Mailerfind
6. [x] Identificado: findings.md pendiente de convertir en archivo transversal

### Hallazgos Clave
- SSH heredoc PowerShell @'..'@ strips Python double quotes -> usar MCP GitHub o python3 para escribir archivos
- Llave SSH correcta: D:\Openclaw\Clave-Ollama\Ollama.pem (no openclaw_key.pem)
- Output actual (10 followers de clinicavesaliooficial) tiene website: null en todos
  -> Target mal para B2B. Usar hashtags de rubro (#dentistaperu) en vez de followers de clinica
- Mailerfind usa 1 credito por batch (no por perfil) -> 10k creditos/mes = ~70k perfiles

### Decisiones Tomadas
- Stack confirmado: FastAPI EC2 + PostgreSQL Supabase + Supabase Auth + Stripe + Resend
- No replicar: InboxKit, Firebase RTDB, Ace Editor, academia de Mailerfind
- Proxima accion: probar hashtag extractor con targets B2B reales

### Pendiente
- [ ] git pull en EC2 (archivos con quotes correctas estan en GitHub)
- [ ] Probar: python3 main.py hashtag dentistaperu --amount 20 --csv
- [ ] findings.md -> archivo transversal de research (sesion futura)
