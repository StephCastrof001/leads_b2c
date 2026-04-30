# PLAN MAESTRO: ORQUESTADOR DE LEADS (CAPA 2) - FORTIFICADO

## 🎯 RESUMEN ESTRATÉGICO
Migración de un scraper básico a una infraestructura resiliente de alta velocidad con foco en Lima, Perú.

## 🛡️ 1. CAPA DE RESILIENCIA (URGENTE)
- **Rotación de Sesiones:** Array de IG_SESSION_IDS.
- **Smart Backoff:** 5-15 min entre distritos.
- **Alertas:** Integración con Telegram/Slack para fallos de sesión o créditos.

## 🔍 2. EXTRACCIÓN Y NORMALIZACIÓN PRO
- **IG Scraper Autenticado:** Uso de cookies para entrar a perfiles de competidores (ej. Clinica Vesalio).
- **Firecrawl Deep Mode:** Crawling de /contacto y /nosotros.
- **Regex Perú:** Normalización de fijos Lima (01) y celulares (9XX).

## 🗄️ 3. SUPABASE & DEDUPLICACIÓN
- **UNIQUE Constraints:** Aplicar en 'ig_handle' y 'email' antes de escalar.
- **Mapeo de Distrito:** Campo obligatorio para segmentación comercial en Lima.

## 🚀 PRÓXIMOS PASOS
1. Aplicar ALTER TABLE para UNIQUE constraints.
2. Implementar módulo de rotación de sesiones.
3. Configurar bot de monitoreo.
