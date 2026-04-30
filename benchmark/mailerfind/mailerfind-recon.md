# Mailerfind — Recon Competitivo
> Fecha: 2026-04-26 | Método: análisis público de JS bundle + scraping de páginas públicas

---

## Stack Confirmado

### Frontend
| Capa | Tecnología | Evidencia |
|---|---|---|
| Framework | **React (Create React App)** | `/static/js/main.177e3b1a.js`, mensaje "You need to enable JavaScript" |
| UI/CSS | **Bootstrap 5** + Htmlstream "Front" admin template | clases Bootstrap, `hs-navbar-vertical-aside`, `htmlstream.com` assets |
| Legacy JS | **jQuery** + jquery-migrate | vendor scripts en HTML |
| Editor HTML | **Ace Editor** (100+ language modes, 30+ themes) | asset-manifest.json |
| Editor Rich Text | **Quill.js** | URL en bundle |
| Auth SDK | **Firebase JS SDK** | `firebaseUser.*`, `getIdToken` |

### Backend
| Capa | Tecnología | Evidencia |
|---|---|---|
| **API** | Firebase Cloud Functions (Node.js) | `us-central1-mailerfind.cloudfunctions.net/mailerfindAPI` |
| **Auth** | Firebase Authentication | `authDomain: mailerfind.firebaseapp.com`, OAuth Google/Facebook/Microsoft |
| **Realtime DB** | Firebase Realtime Database | `mailerfind-default-rtdb.firebaseio.com` |
| **Storage** | Firebase Storage | `storageBucket: mailerfind.appspot.com` |
| **Payments** | Stripe (Clover edition) | `js.stripe.com/clover/stripe.js` |

### Firebase Projects
- **Prod**: `projectId: mailerfind` | `authDomain: mailerfind.firebaseapp.com` | `apiKey: REDACTED_API_KEY`
- **Dev**: `projectId: mailerfind-dev` | `authDomain: mailerfind-dev.firebaseapp.com` | `apiKey: REDACTED_API_KEY`

### Auth Flow
```
Usuario login (email/Google/FB/Microsoft)
        ↓
Firebase Auth → Firebase ID Token (JWT)
        ↓
Frontend: Authorization: Bearer <firebase_id_token>
        ↓
Cloud Function verifica token con Firebase Admin SDK
        ↓
API responde con datos
```

---

## Mapa Completo de API (`/v1/`)

### Instagram Scraping
```
GET  /v1/instagram/search-users
GET  /v1/instagram/search-hashtags
GET  /v1/instagram/search-places
GET  /v1/instagram/get-hashtag-info
GET  /v1/instagram/get-location-info
GET  /v1/instagram/get-media-info
GET  /v1/instagram/get-similar-accounts
GET  /v1/instagram/get-user-media
GET  /v1/instagram/user/{id}
```

### Análisis / Lead Scraping Pipeline
```
POST /v1/queue/add-analysis
GET  /v1/analysis/{id}
DEL  /v1/analysis/bulk-delete
```

### Prospects / Leads
```
GET  /v1/prospects
GET  /v1/prospects/{id}
GET  /v1/lists
GET  /v1/lists/{id}
POST /v1/senders/csv-import
GET  /v1/senders/csv-template
DEL  /v1/senders/bulk-delete
```

### Email Campaigns
```
POST /v1/email/start-campaign
POST /v1/email/pause-campaign
POST /v1/email/send-example
GET  /v1/inbox
```

### Mailboxes (cuentas email propias)
```
GET  /v1/mailboxes/types
GET  /v1/mailboxes/sync-status
GET  /v1/mailboxes/provisioning-limits
GET  /v1/mailboxes/domains/search
POST /v1/mailboxes/orders
GET  /v1/mailboxes/orders/{id}
```

### AI Features
```
POST /v1/ai/email/generate-cold-emails
POST /v1/ai/email/improve-content
POST /v1/ai/email/change-content-tone
POST /v1/ai/email/translate-content
POST /v1/ai/generate-business-description
POST /v1/ai/screenshot
GET  /v1/ai/credits
```

### Enrichment
```
GET  /v1/enrichment/presets
GET  /v1/enrichment/presets/{id}
POST /v1/enrichment/preview
POST /v1/enrichment/start
```

### Billing (Stripe)
```
GET  /v1/stripe/get-my-subscription
GET  /v1/stripe/get-payment-methods
GET  /v1/stripe/list-all-invoices
POST /v1/stripe/buy-credits
POST /v1/stripe/buy-ai-credits
POST /v1/stripe/change-plan
POST /v1/stripe/cancel-subscription
POST /v1/stripe/freeze-subscription
POST /v1/stripe/create-checkout-session
POST /v1/stripe/create-customer-portal-session
POST /v1/stripe/apply-discount
POST /v1/stripe/apply-days-free
POST /v1/stripe/annual-upsell-offer
# Add-ons
POST /v1/stripe/addons/parallel_analysis/purchase
POST /v1/stripe/addons/speed/purchase
POST /v1/stripe/addons/queue/purchase
```

### Auth
```
POST /v1/auth/
POST /v1/auth/google
POST /v1/auth/facebook
POST /v1/auth/microsoft/connect
```

### Otros
```
GET  /v1/accounts
GET  /v1/account-finder
GET  /v1/events/active
GET  /v1/milestones
GET  /v1/pricing/plans
GET  /v1/pricing/price-id
GET  /v1/projects
POST /v1/invitations/create
POST /v1/invitations/accept
GET  /v1/invitations
GET  /v1/chat
GET  /v1/chat/conversations/main
GET  /v1/media/fetch
```

---

## Pricing (Confirmado)
| Plan | Precio | Credits/mes | Email accounts | Emails/mes |
|---|---|---|---|---|
| Starter | €97/mes | 10,000 | 10 | 4,000 |
| Enterprise | €297/mes | 40,000 | 30 | 10,000 |
| Unlimited | €997/mes | Ilimitado | Ilimitado | Ilimitado |
| Managed | Custom | Custom | Custom | Custom |

**Add-ons detectados en API**: `parallel_analysis`, `speed`, `queue` → venden aceleradores de scraping como productos separados.

---

## Integraciones Externas
| Servicio | Propósito |
|---|---|
| SendGrid | Setup email sender (los usuarios conectan su cuenta) |
| MillionVerifier | Verificación de emails |
| Instantly.ai | Export de leads a cold email tool |
| Smartlead | Export de leads a cold email tool |
| Crisp | Support chat en app |
| Cal.com | Booking consultoría en funnel |
| Firebase App Check | Anti-abuse en API calls |

---

## Analytics Stack
- Facebook Pixel
- TikTok Pixel
- Microsoft Clarity (heatmaps/recordings)
- Google Tag Manager (GTM-548CWX6)
- Google Analytics 4 (G-SV7RWEK0L5)

---

## Dominios del Ecosistema
- `app.mailerfind.com` — SPA principal
- `mailerfind.com` — Marketing site (WordPress + WPML)
- `academy.mailerfind.com` — Academia/cursos
- `affiliates.mailerfind.com` — Programa afiliados
- `help.mailerfind.com` — Docs/Help center
- `landing.mailerfind.com` — Landing pages de ofertas
- `mailerfindstatus.com` — Status page

---

## Propuesta de Arquitectura — Tu Producto vs Mailerfind

### Lo que ya tienes (EC2 107.21.24.49)
- Scraper Instagram funcional (login_by_sessionid)
- Extrae followers + bio + website
- Output JSON

### Lo que necesitas agregar para competir

```
[Instagram Scraper — ya tienes esto]
        ↓
[Email Extractor Pipeline]        ← siguiente paso
        ↓
[Lead Database (PostgreSQL)]      ← credits, listas, campañas
        ↓
[Email Sender (SES/Postmark)]     ← warmup + seguimiento
        ↓
[API REST (FastAPI/Node)]         ← rutas /v1/ similares
        ↓
[Frontend React + Auth]           ← interfaz de usuario
```

### Decisión de stack recomendada (vs Mailerfind)
| Capa | Mailerfind | Tu opción | Ventaja tuya |
|---|---|---|---|
| Auth | Firebase Auth | Firebase Auth o Supabase Auth | Igual o mejor con Supabase |
| Backend | Cloud Functions (Node) | FastAPI (Python) en EC2 | Ya tienes EC2, más control |
| DB | Firebase RT DB | PostgreSQL (Supabase) | SQL > NoSQL para datos estructurados |
| Scraping | Infraestructura propia | Tu EC2 actual | Ya funciona |
| Email | Mailboxes propios | Resend/SES + warmup | Más barato al inicio |
| Payments | Stripe | Stripe | Igual |

---

*Recon hecho con análisis de JS bundle público — sin acceso no autorizado.*

---

## Datos Reales de API (autenticado — cuenta free)
> Obtenido via Firebase REST Auth + Bearer JWT directo al backend

### Schema de Prospect (Firestore)
```json
{
  "is_business": false,
  "is_private": false,
  "website": null,
  "city": null,
  "verified": false,
  "verified_type": null,
  "biography": "...",
  "analysis": ["SpMkSYd5y0VwkIOO6ivL"],
  "createdAt": { "_seconds": 1777245458, "_nanoseconds": 742000000 },
  "scraped_at": { "_seconds": 1777245458, "_nanoseconds": 742000000 },
  "followers": 6398,
  "following": 3762,
  "full_name": "...",
  "cover_pic_url": null,
  "profile_pic_url": "https://scontent-waw2-2.cdninstagram.com/...",
  "sourceType": "instagram",
  "phone_number": null,
  "phone_extension": null,
  "pk": 30713458,
  "category": null,
  "email": null,
  "username": "rb12war",
  "id": "cmIxMndhcg=="
}
```
**Nota**: `id` = base64(username). Timestamps = Firestore format.

### Schema de Analysis (job de scraping)
```json
{
  "version": 3,
  "name": "Seguidores de @qr.eterno",
  "selectedItem": { "pk": "44991294991", "username": "qr.eterno", ... },
  "mode": "followers",
  "status": "COMPLETED",
  "isCloud": true,
  "project": null,
  "prospectsCount": 7,
  "publicAccountsCount": 1,
  "privateAccountsCount": 6,
  "businessAccountsCount": 0,
  "emailsFoundCount": 0,
  "phoneNumbersFoundCount": 0,
  "websitesFoundCount": 0,
  "creditsUsed": 1,
  "page": 0,
  "consecutiveBatchFailures": 0,
  "noCursorRetryCount": 0,
  "createdAt": { "_seconds": 1777245418, "_nanoseconds": 576000000 },
  "completedAt": { "_seconds": 1777245459, "_nanoseconds": 11000000 },
  "sourceType": "instagram",
  "id": "SpMkSYd5y0VwkIOO6ivL"
}
```
**Modos de analysis**: `followers`, `likers`, `commenters`, `hashtag`, `location` (inferido del bundle)

### Sistema de Créditos Real
- 1 credit ≠ 1 perfil → es por **batch** (7 perfiles = 1 crédito)
- AI credits separados: pool independiente (free = 50 AI credits, no recarga mensual)
- Mailboxes: plan free = 0 dominios, 5 mailboxes/dominio cuando upgrades

### Mailboxes — Proveedor: InboxKit
| Tipo | Precio dominio | Precio mailbox | Delivery |
|---|---|---|---|
| Google Workspace | €10 | €4.99/mes | 99% / 1 día |
| Microsoft 365 | €10 | €4.99/mes | 99% / 1 día |
| Azure Enterprise | €10 | €31/mes | 99% / 1 día |

**No construyen infraestructura email — revenden InboxKit.**

### Conversión Funnel (datos reales)
- Welcome coupon: **40% descuento** (couponId: W3PYuEoc)
- Urgencia en capas: tier1 (22h) → general (5 días)
- Bonus stack "valorado en €497": campaignReview, antiSpamChecklist, growthClass, metaAdsMasterclass, emailTemplatesPack, subjectLinesPack
- Annual boost: hasta 50% descuento adicional (max 90% combinado)

### Pricing Real con Stripe Price IDs
| Plan | EUR/mes | USD/mes | EUR/año | USD/año |
|---|---|---|---|---|
| Starter | €97 | $97 | €1,164 | — |
| Enterprise | €297 | — | €3,564 | — |
| Unlimited | €997 | **$497** | €11,964 | $4,970 |

**USD Unlimited = $497 vs EUR €997 — mitad de precio para mercado anglófono.**

### Insights Competitivos Clave
1. **creditsUsed: 1 para 7 perfiles** → plan Starter (10k credits) = ~70,000 perfiles
2. **`isCloud: true`** → flag que separa procesamiento cloud de scraping local (legacy)
3. **`version: 3`** del analysis engine → 3 iteraciones del feature core
4. **Firebase Firestore** para datos de prospects (no RTDB)
5. **InboxKit** como proveedor de mailboxes — dependencia de tercero crítica
6. **Blacklisted users** en events: `ignacio@avory.net`, `testings@mailerfind.com` → cuentas internas de testing bloqueadas de promotions
