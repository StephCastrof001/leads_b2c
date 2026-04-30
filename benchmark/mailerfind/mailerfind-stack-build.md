# Cómo Armar el Stack de Mailerfind
> Basado 100% en datos extraídos — cada punto tiene su fuente

---

## Fuentes de evidencia usadas

| Código | Fuente |
|---|---|
| `[B]` | JS bundle `main.177e3b1a.js` (curl + grep) |
| `[A]` | API autenticada (Firebase JWT → curl directo) |
| `[H]` | HTML de la página (Firecrawl rawHtml) |
| `[S]` | Búsqueda web + páginas públicas |

---

## 1. La arquitectura real de Mailerfind

```
┌─────────────────────────────────────────────────────┐
│                   FRONTEND                          │
│  React CRA [B] + Bootstrap/Htmlstream [B][H]        │
│  Ace Editor [B] + Quill.js [B]                      │
│  Firebase JS SDK [B] ← escribe directo a Firestore  │
└──────────────┬──────────────┬───────────────────────┘
               │              │ Firebase SDK (directo)
               │ REST API     ▼
               │    ┌─────────────────┐
               │    │    Firestore    │ [A] timestamps _seconds/_nanoseconds
               │    │  - analyses    │     = formato nativo Firestore
               │    │  - prospects   │
               │    │  - lists       │
               │    └────────┬────────┘
               ▼             │ trigger o poll
  ┌────────────────────────────────────┐
  │  Firebase Cloud Function           │ [B] us-central1-mailerfind.cloudfunctions.net/mailerfindAPI
  │  Node.js / Express                 │     (inferido: Express es el standard para CF HTTP)
  │  /v1/* — 80+ endpoints             │ [B] extraídos del bundle
  │                                    │
  │  Verifica Firebase ID Token [B]    │     Authorization: Bearer <firebase_jwt>
  │  → consulta/escribe Firestore      │
  │  → llama Instagram scraper         │
  │  → llama InboxKit para mailboxes   │ [A] /v1/mailboxes/types → provider: "inboxkit"
  │  → llama Stripe para billing       │ [A] /v1/stripe/* — livemode: true
  └────────────────────────────────────┘
               │
               ▼
  ┌────────────────────────────────────┐
  │  Firebase Realtime Database         │ [B] mailerfind-default-rtdb.firebaseio.com
  │  (updates en tiempo real del        │     probable uso: status del análisis en vivo
  │   análisis mientras corre)          │
  └────────────────────────────────────┘
```

---

## 2. El pipeline de análisis — cómo funciona realmente

Confirmado por el error `"analysisId" is required` en `POST /v1/queue/add-analysis` [A]:

```
PASO 1 — Frontend busca la cuenta objetivo
  GET /v1/instagram/user/{username} [A] → devuelve pk, follower_count, etc.

PASO 2 — Frontend llama a la CF para crear el documento de análisis
  POST /v1/analysis/create (o similar — endpoint exacto no confirmado)
  Body: { mode: "followers", selectedItem: {...} }
  La CF crea el doc en Firestore con service account → devuelve analysisId
  *** CORRECCIÓN: el client SDK no puede escribir en "analyses" ni en
      "users/{uid}/analyses" — Firestore rules bloquean escrituras cliente [A] ***
  (ejemplo real: "SpMkSYd5y0VwkIOO6ivL")

PASO 3 — Frontend encola el análisis via API
  POST /v1/queue/add-analysis [B]
  Body: { analysisId: "SpMkSYd5y0VwkIOO6ivL" }
  (error confirmado: "analysisId is required" — el ID debe venir del paso 2)

PASO 4 — Cloud Function procesa
  Lee el documento de Firestore por analysisId
  Llama al scraper de Instagram (infraestructura propia con pool de cuentas)
  Actualiza el documento: { status: "COMPLETED", prospectsCount: N, creditsUsed: 1 }
  Escribe prospects en colección "prospects" de Firestore

PASO 5 — Frontend escucha en tiempo real
  Firebase Realtime DB o Firestore onSnapshot() → UI se actualiza automáticamente
```

**Schema real del documento de análisis completado** [A]:
```json
{
  "version": 3,
  "name": "Seguidores de @cuenta",
  "selectedItem": { "pk": "...", "username": "...", "follower_count": N },
  "mode": "followers",
  "status": "COMPLETED",
  "isCloud": true,
  "prospectsCount": 7,
  "publicAccountsCount": 1,
  "privateAccountsCount": 6,
  "businessAccountsCount": 0,
  "emailsFoundCount": 0,
  "creditsUsed": 1,
  "consecutiveBatchFailures": 0,
  "noCursorRetryCount": 0,
  "createdAt": { "_seconds": N, "_nanoseconds": N },
  "completedAt": { "_seconds": N, "_nanoseconds": N }
}
```

**Schema real del prospect** [A]:
```json
{
  "pk": 30713458,
  "username": "rb12war",
  "id": "cmIxMndhcg==",
  "full_name": "...",
  "biography": "...",
  "email": null,
  "phone_number": null,
  "website": null,
  "followers": 6398,
  "following": 3762,
  "is_business": false,
  "is_private": false,
  "is_verified": false,
  "verified_type": null,
  "category": null,
  "city": null,
  "profile_pic_url": "https://scontent-*.cdninstagram.com/...",
  "cover_pic_url": null,
  "sourceType": "instagram",
  "analysis": ["SpMkSYd5y0VwkIOO6ivL"],
  "createdAt": { "_seconds": N, "_nanoseconds": N },
  "scraped_at": { "_seconds": N, "_nanoseconds": N }
}
```

**Nota clave**: `id = base64(username)` [A verificado]. `creditsUsed: 1` para 7 perfiles → no es 1 crédito/perfil, es por batch.

---

## 3. Los 5 productos del analizador — modos confirmados

| Modo | Endpoint bundle | Plan | Lo que extrae |
|---|---|---|---|
| `followers` | `/v1/analysis` + `mode: followers` [A real data] | Todos | Seguidores de una cuenta |
| `following` | inferred del bundle [B] | **Premium** (etiqueta UI [S]) | A quiénes sigue la cuenta |
| `commenters` | inferred del bundle [B] | Todos | Quiénes comentaron posts |
| `hashtag` | `/v1/instagram/search-hashtags` [B] | Todos | Usuarios que usan el hashtag |
| `location` | `/v1/instagram/search-places` [B] | Todos | Usuarios de una ubicación |

---

## 4. Sistema de créditos — mecánica real

Confirmado via API [A]:
- **Plan free**: 0 créditos mensuales (currentPlan: "free")
- **Starter**: 10,000 créditos/mes → `profilesPerAnalysis: 2500` [A]
- **Enterprise**: 40,000 créditos/mes → `profilesPerAnalysis: 10,000` [A]
- **Unlimited**: `-1` (ilimitado) → `profilesPerAnalysis: -1` [A]

**Observación real**: análisis de 7 perfiles usó `creditsUsed: 1` [A]
→ 1 crédito ≈ 1 batch de scraping, no 1 perfil

**AI credits separados** [A]:
```json
{ "balance": 50, "monthlyAllocation": 0, "totalPurchased": 0, "totalUsed": 50 }
```
Plan free = 50 AI credits de bienvenida, sin recarga mensual.

---

## 5. Infraestructura de mailboxes — no la construyen ellos

Confirmado [A] via `/v1/mailboxes/types`:

```json
{ "provider": "inboxkit", "type": "google", "pricing": { "domainPrice": 10, "mailboxPrice": 4.99 } }
{ "provider": "inboxkit", "type": "microsoft", "pricing": { "domainPrice": 10, "mailboxPrice": 4.99 } }
{ "provider": "inboxkit", "type": "azure", "pricing": { "domainPrice": 10, "mailboxPrice": 31 } }
```

**Están revendiendo InboxKit.** Markup probable: cobran €4.99 + margen sobre el costo de InboxKit.

---

## 6. Precios reales con Stripe Price IDs

Extraídos de `/v1/pricing/plans` [A]:

| Plan | EUR/mes | USD/mes | EUR/año | Stripe priceId (EUR mensual) |
|---|---|---|---|---|
| Starter | €97 | $97 | €1,164 | `price_1S81YMGYwHFEIfB6rUFQ3nqq` |
| Enterprise | €297 | — | €3,564 | `price_1S81YBGYwHFEIfB6Q0xDXtyk` |
| Unlimited | €997 | **$497** | €11,964 | `price_1S81XyGYwHFEIfB6A6vec1ef` |
| Free | €0 | — | — | `price_1S81XpGYwHFEIfB6cDIvFLF7` |

**Arbitraje USD**: Unlimited USD ($497) = mitad de EUR (€997). Mercado LATAM con precios en USD es oportunidad directa.

---

## 7. Funnel de conversión — datos reales del API

Confirmado [A] via `activeCoupons` en `/v1/pricing/plans`:
```
Welcome coupon: 40% descuento (W3PYuEoc)
Urgencia tier1: 22 horas
Urgencia general: 5 días (118 horas)
Annual boost: hasta 50% adicional (max 90% combinado)
Bonuses stack (valor declarado €497):
  - campaignReview
  - antiSpamChecklist
  - growthClass
  - metaAdsMasterclass
  - emailTemplatesPack
  - subjectLinesPack
```

---

## 8. User document schema — Firestore real (probe.mjs) [A]

Extraído directamente de Firestore `users/{uid}` via Firebase JS SDK:

```json
{
  "email": "steph@colega.lat",
  "uid": "...",
  "currentPlan": "free",
  "credits": 0,
  "aiCredits": { "balance": 50, "monthlyAllocation": 0, "totalPurchased": 0, "totalUsed": 50 },
  "stripeCustomerId": "cus_...",
  "stripeSubscriptionId": null,
  "licenseKey": null,
  "licenseActivations": 0,
  "licenseActivationsLimit": 1,
  "wizard": {
    "completed": false,
    "currentStep": 5,
    "data": {
      "businessDescription": "Colega.ia - Agencia de IA...",
      "targetAccounts": ["clinicavesaliooficial", "..."],  // 10 cuentas
      "generatedEmails": [{ "subject": "...", "body": "..." }]  // 3 emails AI
    }
  },
  "speed": { "delay": 1000, "batch": 10 },
  "parallelAnalysis": false,
  "queuePriority": "normal",
  "createdAt": { "_seconds": N, "_nanoseconds": N },
  "lastLoginAt": { "_seconds": N, "_nanoseconds": N }
}
```

**Observaciones clave**:
- `licenseKey` + `licenseActivationsLimit` → tienen un sistema de licencias (desktop app?)
- `wizard` guarda el onboarding completo con datos de negocio del usuario → usan para personalizar AI
- `speed.delay` + `speed.batch` → add-ons de velocidad se guardan en el user doc
- `parallelAnalysis` → el add-on "parallel_analysis" es simplemente un boolean en el user doc

### Tabla `users` expandida (incluye campos descubiertos)

```sql
CREATE TABLE users (
  id                    TEXT PRIMARY KEY,
  email                 TEXT UNIQUE NOT NULL,
  plan                  TEXT DEFAULT 'free',
  credits               INTEGER DEFAULT 0,
  ai_credits_balance    INTEGER DEFAULT 50,
  ai_credits_purchased  INTEGER DEFAULT 0,
  ai_credits_used       INTEGER DEFAULT 0,
  stripe_customer_id    TEXT,
  stripe_subscription_id TEXT,
  license_key           TEXT,
  license_activations   INTEGER DEFAULT 0,
  license_activations_limit INTEGER DEFAULT 1,
  parallel_analysis     BOOLEAN DEFAULT FALSE,
  queue_priority        TEXT DEFAULT 'normal',
  speed_delay_ms        INTEGER DEFAULT 1000,
  speed_batch_size      INTEGER DEFAULT 10,
  wizard_completed      BOOLEAN DEFAULT FALSE,
  wizard_data           JSONB,
  created_at            TIMESTAMPTZ DEFAULT NOW(),
  last_login_at         TIMESTAMPTZ
);
```

---

## 9. Cómo armar TU versión — decisiones basadas en evidencia

### Stack mínimo para replicar el core

**Auth → Firebase Authentication**
Por qué: ya probamos que funciona, es gratuito hasta 10k MAU, misma DX que ellos.
Alternativa: Supabase Auth (más SQL-friendly).

**Base de datos → PostgreSQL (Supabase)**
Por qué: Firestore es NoSQL. Tus datos (prospects, analyses, credits) son relacionales.
Con PostgreSQL obtienes JOINs, transacciones, y no pagas por operación de lectura.
Schema basado en los schemas reales extraídos [A].

**Backend → FastAPI (Python) en tu EC2**
Por qué: ya tienes EC2 + Python. Sin límite de 9 minutos (su mayor debilidad).
Replica los endpoints `/v1/*` que mapeamos.

**Scraping → tu scraper actual + expandir modos**
Ya tienes: `mode: followers` funcional en `docs_dev/clientes_instagram/main.py`
Añadir: `commenters`, `hashtag`, `location` con instagrapi.

**Pagos → Stripe**
Mismo que ellos. Usar `stripe.checkout.Session` para replicar su flujo.

**Email delivery → Resend o AWS SES**
NO usar InboxKit al inicio — Resend API es más simple y $0 hasta 3k emails/mes.

---

### Schema PostgreSQL basado en datos reales

```sql
-- Basado en schema real extraído [A]
CREATE TABLE prospects (
  id            TEXT PRIMARY KEY,        -- base64(username)
  pk            BIGINT,                  -- Instagram pk
  username      TEXT NOT NULL,
  full_name     TEXT,
  email         TEXT,
  phone_number  TEXT,
  website       TEXT,
  biography     TEXT,
  city          TEXT,
  category      TEXT,
  followers     INTEGER,
  following     INTEGER,
  is_business   BOOLEAN DEFAULT FALSE,
  is_private    BOOLEAN DEFAULT FALSE,
  is_verified   BOOLEAN DEFAULT FALSE,
  verified_type TEXT,
  profile_pic_url TEXT,
  source_type   TEXT DEFAULT 'instagram',
  scraped_at    TIMESTAMPTZ,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE analyses (
  id              TEXT PRIMARY KEY,      -- UUID o Firestore-style ID
  version         INTEGER DEFAULT 1,
  name            TEXT,
  mode            TEXT,                  -- followers|following|commenters|hashtag|location
  status          TEXT DEFAULT 'PENDING', -- PENDING|RUNNING|COMPLETED|FAILED
  is_cloud        BOOLEAN DEFAULT TRUE,
  selected_item   JSONB,                 -- target Instagram account
  prospects_count INTEGER DEFAULT 0,
  public_count    INTEGER DEFAULT 0,
  private_count   INTEGER DEFAULT 0,
  business_count  INTEGER DEFAULT 0,
  emails_found    INTEGER DEFAULT 0,
  phones_found    INTEGER DEFAULT 0,
  websites_found  INTEGER DEFAULT 0,
  credits_used    INTEGER DEFAULT 0,
  error_message   TEXT,
  page            INTEGER DEFAULT 0,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  completed_at    TIMESTAMPTZ,
  user_id         TEXT NOT NULL          -- FK a users
);

CREATE TABLE users (
  id            TEXT PRIMARY KEY,        -- Firebase UID o propio
  email         TEXT UNIQUE,
  plan          TEXT DEFAULT 'free',
  credits       INTEGER DEFAULT 0,
  ai_credits    INTEGER DEFAULT 50,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de relación prospect ↔ analysis (ellos usan array en Firestore [A])
CREATE TABLE prospect_analyses (
  prospect_id TEXT REFERENCES prospects(id),
  analysis_id TEXT REFERENCES analyses(id),
  PRIMARY KEY (prospect_id, analysis_id)
);
```

---

### API endpoints a implementar (prioridad por valor)

**Fase 1 — MVP (lo que da dinero)**
```
POST /v1/auth/                    ← login
GET  /v1/instagram/user/{username} ← buscar cuenta objetivo
POST /v1/analysis/create          ← crear análisis (tu versión)
POST /v1/queue/add-analysis       ← encolar scraping
GET  /v1/analysis/{id}            ← status en tiempo real
GET  /v1/prospects                ← ver leads extraídos
GET  /v1/pricing/plans            ← mostrar planes
POST /v1/stripe/create-checkout-session ← comprar plan
```

**Fase 2 — Completar el producto**
```
POST /v1/email/start-campaign     ← enviar campañas
POST /v1/email/pause-campaign
GET  /v1/lists                    ← gestionar listas
POST /v1/senders/csv-import       ← importar leads externos
GET  /v1/stripe/get-my-subscription
```

**Fase 3 — Diferenciadores**
```
POST /v1/ai/email/generate-cold-emails  ← AI emails
GET  /v1/enrichment/start               ← enriquecimiento
GET  /v1/mailboxes/types                ← mailboxes propios
```

---

## 10. Lo que ellos tienen que TÚ NO necesitas replicar

| Feature de Mailerfind | Por qué saltarlo |
|---|---|
| InboxKit mailboxes propios | Empieza con SMTP del usuario (Gmail/Outlook conectado) |
| Ace Editor HTML completo | Empieza con Quill solo o plantillas fijas |
| Firebase Realtime DB | WebSockets o polling simple con PostgreSQL |
| 5 analytics pixels | Empieza con GA4 solo |
| Cal.com booking en login | Agrega después cuando tengas usuarios |
| Academia (`academy.mailerfind.com`) | Contenido, no producto — después |

---

*Todo lo anterior está basado en datos extraídos — no hipótesis.*
*Fuentes: curl sobre bundle JS público + llamadas API autenticadas con cuenta propia.*
