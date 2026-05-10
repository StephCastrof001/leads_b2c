# ðŸ“¦ PRD: SaaS Agent Pipeline (Data B2B)
## DivisiÃ³n de Funciones: Antigravity (Frontend) + Claude (Backend)

---

## ðŸŽ¯ Producto
**Una fÃ¡brica de leads B2B para LatAm.** El usuario (agencia/vendedor) obtiene leads de dos formas:

1. **ðŸ“¦ Paquetes Pre-armados** â€” Listas listas por sector (Inmobiliarias Lima, ClÃ­nicas CDMX, etc.). Compra y descarga al instante.
2. **ðŸŽ¯ Pedido Custom (On-Demand)** â€” El usuario dice: Dame los comentaristas de @clinica_rival que preguntaron 'precio' en los Ãºltimos 30 dÃ­as. Entrega en 48h.

---

## ðŸ—ï¸ Tech Stack

| Capa | TecnologÃ­a | QuiÃ©n lo arma |
|------|-----------|---------------|
| **Frontend** | Vite + React + Stitch (UI) | **Antigravity** |
| **Backend API** | Python FastAPI | **Claude** |
| **Scraping** | Apify Actors + Proxies | **Claude** |
| **Base de Datos** | Supabase (PostgreSQL) | **Claude** |
| **Auth** | Supabase Auth | **Claude** |
| **Pagos** | Stripe / Mercado Pago | **Claude** |
| **Storage** | Supabase Storage (CSVs) | **Claude** |

---

## ðŸ‘¥ User Stories (MVP)

| # | Como... | Quiero... | Para... |
|---|---------|-----------|---------|
| US-1 | Gerente de Ventas | Ver un catÃ¡logo de paquetes de leads por sector | Elegir quÃ© lista comprar al instante |
| US-2 | Gerente de Ventas | Pagar con tarjeta o Mercado Pago | Obtener mi lista al instante |
| US-3 | Gerente de Ventas | Descargar un CSV con nombre, telÃ©fono, email, fuente | Importarlo a mi CRM/WhatsApp |
| US-4 | Gerente de Ventas | **Pedir un extracto custom** de una cuenta de IG/TikTok especÃ­fica | Obtener leads hiper-relevantes de mi competidor directo |
| US-5 | Admin (tÃº) | Subir listas generadas por los agentes | Que estÃ©n disponibles para venta |
| US-6 | Admin (tÃº) | Ver dashboard de ventas, descargas y pedidos custom | Saber quÃ© se vende y quÃ© pedidos estÃ¡n pendientes |

---

## ðŸ“ Screens (Frontend â€” Antigravity + Stitch)

### Screen 1: Landing Page / Home
- Hero: Leads B2B verificados para LatAm. Descarga tu lista en 5 minutos.
- CatÃ¡logo de paquetes por sector (cards con precio, cantidad, preview)
- Social proof: 2,300 leads entregados este mes
- CTA: Ver Paquetes

### Screen 2: CatÃ¡logo de Paquetes
- Filtros: PaÃ­s, Sector, TamaÃ±o de lista
- Cards: Nombre del paquete, descripciÃ³n, # de leads, precio, botÃ³n Comprar
- Preview: Muestra 5 leads de ejemplo (borrosos/parciales)

### Screen 3: Checkout
- Resumen del pedido
- Formulario de pago (Stripe/MP embed)
- BotÃ³n Pagar y Descargar

### Screen 4: Custom Request (On-Demand) ðŸ†•
- Formulario: Â¿QuÃ© cuenta de IG/TikTok quieres monitorear?
- Campo: URL de la cuenta objetivo
- Campo: Tipo de dato (Comentaristas, Likers, Seguidores)
- Campo: Filtro de keywords (precio, envÃ­o, cita, etc.)
- Precio dinÃ¡mico segÃºn volumen estimado
- CTA: Pedir mi Lista Custom ($X)
- Status tracker: Procesando â†’ Listo para descargar

### Screen 5: Dashboard (Post-compra)
- Historial de compras (paquetes + custom)
- Links de descarga (CSV)
- Estado de pedidos custom (En proceso, Listo)

### Screen 6: Admin Panel (Solo tÃº)
- Subir nuevas listas (CSV upload)
- Crear paquetes (nombre, sector, paÃ­s, precio, archivo)
- **Cola de pedidos custom** (ver, procesar, entregar)
- Ver mÃ©tricas de venta

---

## ðŸ”Œ API Endpoints (Backend â€” Claude)

### Auth
| MÃ©todo | Ruta | DescripciÃ³n |
|--------|------|-------------|
| POST | `/api/auth/register` | Registro con email |
| POST | `/api/auth/login` | Login, retorna JWT |

### Paquetes (PÃºblico)
| MÃ©todo | Ruta | DescripciÃ³n |
|--------|------|-------------|
| GET | `/api/packages` | Listar paquetes disponibles (filtros: paÃ­s, sector) |
| GET | `/api/packages/:id` | Detalle de un paquete + preview de 5 leads |

### Compras (Autenticado)
| MÃ©todo | Ruta | DescripciÃ³n |
|--------|------|-------------|
| POST | `/api/checkout` | Crear sesiÃ³n de pago (Stripe/MP) |
| POST | `/api/webhook/payment` | Webhook de confirmaciÃ³n de pago |
| GET | `/api/purchases` | Historial de compras del usuario |
| GET | `/api/purchases/:id/download` | Generar link temporal de descarga CSV |

### Custom Requests (Autenticado)
| MÃ©todo | Ruta | DescripciÃ³n |
|--------|------|-------------|
| POST | `/api/custom-requests` | Crear pedido custom (cuenta IG + filtros) |
| GET | `/api/custom-requests` | Listar mis pedidos custom |
| GET | `/api/custom-requests/:id` | Estado + descarga del pedido |

### Admin (Solo Admin)
| MÃ©todo | Ruta | DescripciÃ³n |
|--------|------|-------------|
| POST | `/api/admin/packages` | Crear paquete nuevo |
| PUT | `/api/admin/packages/:id` | Editar paquete |
| POST | `/api/admin/packages/:id/upload` | Subir CSV al paquete |
| GET | `/api/admin/custom-requests` | Ver cola de pedidos custom pendientes |
| PUT | `/api/admin/custom-requests/:id/deliver` | Marcar pedido como Listo + subir CSV |
| GET | `/api/admin/metrics` | Dashboard de ventas |

### Agentes / Scraping (Interno)
| MÃ©todo | Ruta | DescripciÃ³n |
|--------|------|-------------|
| POST | `/api/agents/run` | Lanzar un Apify Actor para generar leads |
| GET | `/api/agents/status/:runId` | Ver estado del scraping |

---

## ðŸ“ Estructura de Carpetas

```
d:\habilidades\agent-pipeline/
â”œâ”€â”€ frontend/                    â† ANTIGRAVITY
â”‚   â”œâ”€â”€ .stitch/                 â† DiseÃ±os con Stitch
â”‚   â”‚   â”œâ”€â”€ DESIGN.md
â”‚   â”‚   â”œâ”€â”€ SITE.md
â”‚   â”‚   â”œâ”€â”€ next-prompt.md
â”‚   â”‚   â””â”€â”€ designs/
â”‚   â”œâ”€â”€ src/
â”‚   â”‚   â”œâ”€â”€ pages/
â”‚   â”‚   â”‚   â”œâ”€â”€ Home.jsx
â”‚   â”‚   â”‚   â”œâ”€â”€ Catalog.jsx
â”‚   â”‚   â”‚   â”œâ”€â”€ Checkout.jsx
â”‚   â”‚   â”‚   â””â”€â”€ Dashboard.jsx
â”‚   â”‚   â”œâ”€â”€ components/
â”‚   â”‚   â”‚   â”œâ”€â”€ PackageCard.jsx
â”‚   â”‚   â”‚   â”œâ”€â”€ LeadPreview.jsx
â”‚   â”‚   â”‚   â”œâ”€â”€ NavBar.jsx
â”‚   â”‚   â”‚   â””â”€â”€ PaymentForm.jsx
â”‚   â”‚   â”œâ”€â”€ App.jsx
â”‚   â”‚   â””â”€â”€ main.jsx
â”‚   â”œâ”€â”€ public/
â”‚   â”œâ”€â”€ index.html
â”‚   â”œâ”€â”€ vite.config.js
â”‚   â””â”€â”€ package.json
â”‚
â”œâ”€â”€ backend/                     â† CLAUDE
â”‚   â”œâ”€â”€ app/
â”‚   â”‚   â”œâ”€â”€ main.py              â† FastAPI app
â”‚   â”‚   â”œâ”€â”€ routes/
â”‚   â”‚   â”‚   â”œâ”€â”€ auth.py
â”‚   â”‚   â”‚   â”œâ”€â”€ packages.py
â”‚   â”‚   â”‚   â”œâ”€â”€ checkout.py
â”‚   â”‚   â”‚   â””â”€â”€ admin.py
â”‚   â”‚   â”œâ”€â”€ models/
â”‚   â”‚   â”‚   â”œâ”€â”€ user.py
â”‚   â”‚   â”‚   â”œâ”€â”€ package.py
â”‚   â”‚   â”‚   â””â”€â”€ purchase.py
â”‚   â”‚   â”œâ”€â”€ services/
â”‚   â”‚   â”‚   â”œâ”€â”€ apify_agent.py   â† Orquestador de scraping
â”‚   â”‚   â”‚   â”œâ”€â”€ payment.py       â† Stripe/MP integration
â”‚   â”‚   â”‚   â””â”€â”€ csv_generator.py
â”‚   â”‚   â””â”€â”€ config.py
â”‚   â”œâ”€â”€ requirements.txt
â”‚   â””â”€â”€ .env
â”‚
â”œâ”€â”€ shared/
â”‚   â””â”€â”€ types.ts                 â† Tipos compartidos
â”‚
â””â”€â”€ README.md
```

---

## ðŸ”„ Flujo de Trabajo (QuiÃ©n hace quÃ©, cuÃ¡ndo)

```mermaid
sequenceDiagram
    participant AG as Antigravity (Frontend)
    participant CL as Claude (Backend)
    
    Note over AG,CL: FASE 1 (Paralelo)
    AG->>AG: Scaffold Vite + React
    AG->>AG: DiseÃ±ar con Stitch (Landing, CatÃ¡logo)
    CL->>CL: Scaffold FastAPI + Supabase
    CL->>CL: Crear modelos + endpoints de paquetes
    
    Note over AG,CL: FASE 2 (IntegraciÃ³n)
    CL->>AG: API lista en /api/packages
    AG->>AG: Conectar Catalog.jsx al API
    CL->>CL: Implementar Stripe/MP checkout
    AG->>AG: Integrar formulario de pago
    
    Note over AG,CL: FASE 3 (Admin + Agentes)
    CL->>CL: Panel admin + upload CSV
    CL->>CL: Integrar Apify actors
    AG->>AG: Dashboard post-compra
```

---

## âœ… Checklist de Arranque

### Antigravity (Frontend) â€” AHORA
- [ ] Crear carpeta `d:\habilidades\agent-pipeline\frontend`
- [ ] Scaffold: `npx create-vite@latest ./`
- [ ] Configurar `.stitch/` para diseÃ±o con Stitch
- [ ] DiseÃ±ar Screen 1 (Landing) con Stitch
- [ ] DiseÃ±ar Screen 2 (CatÃ¡logo) con Stitch

### Claude (Backend) â€” DESPUÃ‰S
- [ ] Crear carpeta `d:\habilidades\agent-pipeline\backend`
- [ ] Scaffold: FastAPI + Supabase client
- [ ] Crear modelos: User, Package, Purchase
- [ ] Implementar `GET /api/packages` y `GET /api/packages/:id`
- [ ] Configurar Supabase Auth

