# Instagram Lead Extractor

Extrae datos de usuarios de Instagram por 5 fuentes distintas. Enriquece con Firecrawl para obtener emails reales desde websites en bio.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tu IG_SESSION_ID
```

## 5 Modos de Extraccion

| Modo | Fuente | Comando ejemplo |
|------|--------|-----------------|
| `followers` | Seguidores de una cuenta | `python3 main.py followers clinicavesaliooficial --amount 50` |
| `following` | Cuentas que sigue un usuario | `python3 main.py following nike --amount 20` |
| `comments`  | Comentaristas de un post | `python3 main.py comments https://www.instagram.com/p/ABC123/ --amount 100` |
| `hashtag`   | Usuarios de un hashtag | `python3 main.py hashtag dentistaperu --amount 50` |
| `location`  | Usuarios de una ubicacion | `python3 main.py location 212988663 --amount 50` |

## Flags

- `--amount N` — cuantos perfiles extraer (default: 20)
- `--enrich`   — activa Firecrawl para scrape de websites en bio → emails/phones reales
- `--csv`      — exporta CSV ademas de JSON (para entregar a clientes)

## Estructura

```
clientes_instagram/
├── main.py              ← CLI entry point
├── auth.py              ← manejo de sesion (3-tier: session.json → sessionid → user/pass)
├── enricher.py          ← Firecrawl: website → email/phone
├── export.py            ← guardar JSON + CSV
├── extractors/
│   ├── base.py          ← utilidades compartidas
│   ├── followers.py     ← Seguidores
│   ├── following.py     ← Siguiendo
│   ├── comments.py      ← Comentaristas
│   ├── hashtag.py       ← Hashtag
│   └── location.py      ← Ubicacion
└── output/              ← JSONs y CSVs generados
```

## Sesion de Instagram

Obtener `IG_SESSION_ID` desde Chrome:
1. Instalar Cookie-Editor extension
2. Ir a instagram.com y loguearse
3. Abrir Cookie-Editor → buscar `sessionid` → copiar valor
4. Pegar en `.env` como `IG_SESSION_ID=...`

La sesion se cachea en `session.json`. Si expira, repetir el paso anterior.

## Output

JSON por extraccion en `output/`. Cada perfil incluye:
- `username`, `full_name`, `bio`, `website`
- `followers`, `is_business`
- `emails_in_bio`, `phones_in_bio` — regex en bio
- `emails_web`, `phones_web` — de Firecrawl (si usaste --enrich)
