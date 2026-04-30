# Research: LeadGen Instagram - Mercado LATAM/Peru
*Fecha: 2026-04-26 | Actualizado: 2026-04-27*

---

## Como funcionan realmente los servicios de leads de Instagram?

### Lo que NO hacen
Instagram no expone emails ni telefonos directamente via API.
Nadie extrae emails de Instagram — lo que hacen es enriquecer datos de otras fuentes.

### Tecnicas reales

#### 1. Pattern Mining en Bio
Regex sobre el texto de la bio publica.
Efectividad en Peru: BAJA (pocos usuarios ponen datos en bio)

#### 2. Website Scraping (el modelo real)
Si el perfil tiene website en bio -> scrapear ese sitio -> extraer contacto.
Efectividad: MEDIA-ALTA para cuentas business

#### 3. Google Maps -> Email (el mas efectivo para LATAM)
Google Maps clinicas Lima -> lista de negocios con website -> scrape -> email.
Efectividad: ALTA — los negocios peruanos SI registran email en Maps

#### 4. Cross-referencing
username IG -> buscar en LinkedIn / Facebook / Google.
Efectividad: MEDIA para B2B, BAJA para consumidores

#### 5. Bases de datos compradas
Directorios de empresas, SUNAT RUC publico, LinkedIn scrapes.
Efectividad: ALTA para B2B, zona gris legal

---

## Mapa de Competidores B2C LATAM — Herramientas con presencia en espanol

| Herramienta | Precio | Lo que hace | LATAM real? | Estado recon |
|---|---|---|---|---|
| Growman (Chrome ext.) | Free 500 / pago | Extrae emails de IG por followers, hashtags, ubicaciones. Interfaz en espanol. 4.2★ 256 reviews | Parcial — interfaz ES pero no Peru-first | Pendiente |
| **Mailerfind** | Freemium €97-997/mes | Extrae de followers de cualquier cuenta IG, GDPR compliant, version en espanol. 5 modos: followers/following/commenters/hashtag/location | Si — soporte en espanol, usado en LATAM | **✅ Recon completo** — ver benchmark/mailerfind/ |
| Leadigger | €89/mes | All-in-one: scraping + verificacion + email campaigns. Blog en espanol | Parcial — contenido ES pero no LATAM-niche | Pendiente |
| ExtractorLead | 25 creditos gratis / pago | Email + telefono de IG, LinkedIn, TikTok. Sin login de redes. Built-in email marketing | No — global, en ingles | Pendiente |
| SocialScraper.io | Pay-per-email | Scrape ilimitado de IG, modelo pago por resultado | No — global | Pendiente |
| Scravio | Gratis (extension) | Export followers a CSV/Excel. Sin login requerido. Ilimitado | No — global | Pendiente |
| DolphinRadar | Free tier / pago | IG follower export a CSV, anonimo, sin login | No — global, asiatico | Pendiente |

---

## Insight: Mailerfind es el benchmark principal
Recon completo disponible en benchmark/mailerfind/.
Stack: React + Firebase Cloud Functions + Firestore + InboxKit + Stripe.
Pricing real: Starter €97/mes (10k creditos), Enterprise €297/mes, Unlimited €997/mes.
1 credito = 1 batch (~7 perfiles) — Starter = ~70k perfiles/mes.
Debilidad clave: Cloud Functions tienen limite de 9 min — nuestro EC2 no.

## Insight: InstaLeads NO es lo que parece
InstaLeads (el #1 en habla hispana con 1,600 clientes) NO extrae emails.
Propuesta de valor: sigue automaticamente a seguidores de tu competencia y les manda DM.
Es un bot de engagement, no un extractor de datos.

---

## Estrategia recomendada para el proyecto

### Fase 2 (proxima): Website enrichment
- Para cada follower con website en bio -> Firecrawl -> extraer email/telefono
- Target correcto: cuentas business con website (no clinicas con followers privados)
- Mejor modo: hashtag (#dentistaperu, #tallermecanicolima) > followers de una cuenta

### Fase 3 (alto impacto): Google Maps para Peru
- Google Maps Lima por rubro -> lista de negocios -> website -> email
- Sin dependencia de Instagram — datos mas limpios
- Combinable: Maps da el email, IG da el contexto del negocio

---

## Legalidad en Peru
- Datos publicos en bio/web: zona gris (ToS IG), no ilegal
- Vender lista a terceros sin consentimiento: Ley 29733
- Opt-in propio: completamente legal
