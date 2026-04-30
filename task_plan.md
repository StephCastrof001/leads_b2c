# ROADMAP - Instagram LeadGen Platform
> Basado en recon real de Mailerfind (benchmark/mailerfind/) + estado actual del proyecto

---

## Objetivo
Construir una plataforma de extraccion de leads B2B a partir de Instagram.
Competidor de referencia: Mailerfind (stack confirmado por recon de JS bundle + API autenticada).

---

## Estado actual (2026-04-27)

### Fase 1 COMPLETADA: Scraper CLI
- [x] 5 modos: followers, following, comments, hashtag, location
- [x] Auth 3-tier: session.json > IG_SESSION_ID > user/pass
- [x] Enricher Firecrawl (website en bio -> email/phone)
- [x] Export JSON + CSV
- [x] Repo GitHub: StephCastrof001/clientes_extracciondatos
- [x] EC2 Ubuntu 107.21.24.49

---

## Arquitectura decidida (basada en Mailerfind recon)

| Capa | Decision | Razon |
|---|---|---|
| Auth | Supabase Auth | Gratuito hasta 50k MAU, SQL-friendly |
| Backend | FastAPI en EC2 | Ya tenemos EC2 + Python, sin limite de 9min |
| DB | PostgreSQL (Supabase) | SQL > Firestore NoSQL para datos relacionales |
| Scraping | instagrapi en EC2 | Ya funciona |
| Email | Resend o AWS SES | Gratis hasta 3k/mes, no replicar InboxKit |
| Pagos | Stripe | Igual que Mailerfind |

---

## Schema PostgreSQL (basado en schema real extraido de Mailerfind via API)

```sql
CREATE TABLE users (
  id         TEXT PRIMARY KEY,
  email      TEXT UNIQUE,
  plan       TEXT DEFAULT 'free',
  credits    INTEGER DEFAULT 0,
  ai_credits INTEGER DEFAULT 50,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE analyses (
  id              TEXT PRIMARY KEY,
  name            TEXT,
  mode            TEXT,
  status          TEXT DEFAULT 'PENDING',
  selected_item   JSONB,
  prospects_count INTEGER DEFAULT 0,
  emails_found    INTEGER DEFAULT 0,
  credits_used    INTEGER DEFAULT 0,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  completed_at    TIMESTAMPTZ,
  user_id         TEXT NOT NULL
);

CREATE TABLE prospects (
  id          TEXT PRIMARY KEY,
  pk          BIGINT,
  username    TEXT NOT NULL,
  full_name   TEXT,
  email       TEXT,
  phone       TEXT,
  website     TEXT,
  biography   TEXT,
  followers   INTEGER,
  is_business BOOLEAN DEFAULT FALSE,
  source_type TEXT DEFAULT 'instagram',
  scraped_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE prospect_analyses (
  prospect_id TEXT REFERENCES prospects(id),
  analysis_id TEXT REFERENCES analyses(id),
  PRIMARY KEY (prospect_id, analysis_id)
);
```

---

## Sistema de creditos (mecanica real de Mailerfind)

- 1 credito = 1 batch (no 1 perfil). Starter 10k creditos = ~70k perfiles/mes
- AI credits pool separado (50 gratis al inicio, sin recarga mensual)
- Referencia de precios: Starter $97/mes, Pro $297/mes, Unlimited $497/mes USD

---

## Fases de desarrollo

### Fase 2 SIGUIENTE: Pipeline de Enriquecimiento
- [ ] Correr hashtag extractor con targets B2B reales: #dentistaperu, #tallermecanicolima
- [ ] Confirmar que followers de cuentas business tienen websites en bio
- [ ] CSV entregable a primer cliente proveedor
- [ ] Validar modelo: $50-150 por lista de 200-500 leads con email

### Fase 3: Backend API
- [ ] FastAPI en EC2 con endpoints core:
      POST /v1/analysis/create
      GET  /v1/analysis/{id}
      GET  /v1/prospects
      POST /v1/stripe/create-checkout-session
- [ ] PostgreSQL en Supabase free tier
- [ ] Jobs en background (analisis async, frontend consulta status)

### Fase 4: Auth + Pagos
- [ ] Supabase Auth (email + Google)
- [ ] Stripe checkout con 3 planes (free, starter, pro)
- [ ] Sistema de creditos por plan

### Fase 5: Frontend
- [ ] React + Tailwind
- [ ] 3 pantallas core: buscar cuenta -> ver analisis -> exportar leads

### Fase 6: Email Campaigns (diferenciador futuro)
- [ ] Resend API para envio
- [ ] AI para cold email
- [ ] Plantillas fijas primero, editor despues

---

## Lo que NO replicar de Mailerfind al inicio

| Feature | Por que saltarlo |
|---|---|
| InboxKit mailboxes propios | Empezar con Resend directo |
| Ace Editor HTML | Plantillas fijas primero |
| Firebase Realtime DB | Polling simple con PostgreSQL |
| Academia, afiliados, 5 pixels de analytics | No es producto core |

---

## Modelo de negocio

Hoy: venta directa de listas CSV a proveedores B2B peruanos ($50-150/lista)
Fase media: SaaS con creditos
- Free: 0 creditos/mes
- Starter: $49/mes -> 5,000 leads/mes
- Pro: $149/mes -> 20,000 leads/mes

---

## Nota pendiente: findings.md
Convertir en archivo transversal de research aplicable a cada proyecto con dev tools.
No solo scraping de IG -> incluir: benchmarks, APIs, stacks, mercado LATAM.
(Implementar en sesion futura)

---

*Ultima actualizacion: 2026-04-27*
*Fuentes: benchmark/mailerfind/recon.md + stack-build.md*
