# Research Findings - Lead Generation Platform

## 1. Market Landscape

### Top Herramientas Comerciales
- **Phantombuster**: Líder del mercado, 100+ automations, pricing $29-499/mo
- **IGLeads.io**: Especializado en Instagram/Facebook, cloud-based
- **Lusha**: Enfoque B2B, LinkedIn primary
- **Ziwa**: Pay-per-result modelo, $0.025/contact
- **Bright Data**: Enterprise, Web Unlocker solución completa

### Diferenciadores Clave
- Velocidad de extracción
- Calidad/verificación de datos
- Facilidad de uso
- Cobertura multi-plataforma

## 2. Técnicas de Extracción

### Método 1: Web Scraping Tradicional
- Playwright/Puppeteer para renderizar JS
- Rotación de User Agents
- Proxies residenciales (crucial para evitar bans)
- Rate limiting inteligente

### Método 2: APIs Oficiales
- **Instagram Graph API**: Solo business metadata, NO contact info
- **Facebook Lead Ads**: Solo si el usuario respondió un formulario
- **Conclusión**: APIs oficiales NO proporcionan emails/teléfonos

### Método 3: Data Enrichment Services
- Cross-reference con bases de datos existentes
- LinkedIn profile → Work email
- Public records search

### Método 4: Pattern Mining
- Buscar en bio/description patrones: email, phone
- Extraer de websites vinculados
- Analizar posts/comments

## 3. Limitaciones y Legalidad

### Limitaciones Técnicas
- Instagram/Facebook anti-scraping muy agresivo
- Rate limits estrictos (200 req/hour typical)
- requiere proxies de alta calidad
- Cuentas business más permisivas

### Consideraciones Legales
- **GDPR**: Datos europeos requieren consentimiento
- **CCPA**: Consumidores California
- **Términos de Servicio**: Violación puede resultar en bans
- **CFAA**: Considerado "unauthorized access" en algunos casos

### Best Practices de las Empresas
1. Solo datos públicos
2. Respetar robots.txt
3. Rate limiting
4. No monetizar datos de otros
5. Proxies residenciales (no datacenters)

## 4. Stack Tecnológico Recomendado

### Scraping
- Playwright (más estable que Puppeteer)
- Bright Data o Smartproxy para proxies
- Fingerprint management

### Backend
- Node.js/Express o Python/FastAPI
- PostgreSQL para almacenamiento
- Redis para caché/rate limiting

### Automatización
- n8n para workflows
- API REST para integración

### Frontend
- Next.js + Tailwind
- Dashboard admin

## 5. Complejidad y Timeline Estimado

| Módulo | Complejidad | Timeline |
|--------|-------------|----------|
| Core scraper | Alta | 2-3 semanas |
| Instagram module | Alta | 1-2 semanas |
| Facebook module | Media | 1 semana |
| Data validation | Media | 1 semana |
| Dashboard | Media | 1-2 semanas |
| n8n integration | Baja | 3-5 días |

**Total estimado**: 7-11 semanas para MVP

## 6. Alternativas No-Code
- Make.com + Scraper APIs
- n8n + scraping nodes
- Phantombuster (ya resuelto)
- Zapier + Web Scraper

## 7. Recursos Investigados
- https://profilespider.com/blog/best-tools-for-scraping-leads
- https://igleads.io/resources/best-instagram-email-scraper/
- https://developers.facebook.com/docs/instagram-platform/
- https://www.oxylabs.com/
- https://www.brightdata.com/
