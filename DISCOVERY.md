# Mailerfind B2B Free Search Pipeline

> **Fecha**: 2026-04-30
> **Estado**: Funcionando (Sin costo de créditos)

## El Descubrimiento

Durante el benchmark de la API de Mailerfind, descubrimos que los endpoints que permiten "robar" miles de seguidores de un perfil de una sola vez (`/v1/instagram/followers/{pk}` y `/v1/instagram/following/{pk}`) han sido **parcheados y bloqueados** (ahora devuelven error 404).

Sin embargo, descubrimos un **nuevo pipeline 100% gratis** utilizando los endpoints de "búsqueda" internos de la plataforma, los cuales funcionan como un proxy seguro y anónimo hacia Instagram sin descontar el saldo mensual de créditos.

## Los 3 Endpoints Gratuitos

Estos endpoints no consumen los créditos del plan "Starter/Enterprise":

### 1. Búsqueda de Usuarios (`/v1/instagram/search-users`)
- **Método**: `POST`
- **Body**: `{ "query": "clinica dental lima" }`
- **Retorno**: 5 cuentas de Instagram que coinciden con la búsqueda (username, pk, full_name).

### 2. Búsqueda de Hashtags (`/v1/instagram/search-hashtags`)
- **Método**: `POST`
- **Body**: `{ "query": "odontologiaperu" }`
- **Retorno**: Información del hashtag y volumen de posts (`media_count`).

### 3. Detalle de Perfil (`/v1/instagram/user/{username}`)
- **Método**: `GET`
- **Retorno**: Toda la información pública del perfil:
  - `follower_count`
  - `biography`
  - `external_url` (Linktree, WhatsApp, Website)
  - `public_email` y `public_phone_number` (si los tiene visibles en IG)
  - `category` y `city_name`

## El Pipeline Definitivo (B2B Crawler)

Dado que este flujo nos da negocios (B2B) en lugar de seguidores aleatorios (B2C), armamos un script llamado `search_extractor.mjs` que hace lo siguiente:

1. **Generador de Queries**: Cruza Nichos (Clínicas, Ferreterías, Insumos) × Distritos (Miraflores, Surco, Los Olivos).
2. **Instagram Search**: Hace ping a Mailerfind por cada query, obteniendo cientos de usernames únicos.
3. **Instagram Lookup**: Obtiene la URL (website/linktree) de cada negocio.
4. **Firecrawl Enrichment**: Si hay una URL, usa la API de Firecrawl (`FIRECRAWL_API_KEY`) para leer la página web de la empresa y extraer mediante Regex el **Correo, Teléfono y Dirección**.
5. **Rate Limiting**: Utiliza esperas aleatorias (0.5s - 1.5s) para simular comportamiento humano y evitar baneos por parte de Mailerfind.
6. **Exportación**: Guarda todo en `leads_b2b_lima.json` y `leads_b2b_lima.csv`.

## Limitaciones Conocidas
- El endpoint de búsqueda devuelve máximo 5-10 resultados por cada término de búsqueda. Por eso es obligatorio hacer "permutaciones" (cruzar muchos rubros con muchos distritos).
- Solo obtenemos la data de contacto si la empresa tiene un link web/whatsapp en su perfil de IG.
