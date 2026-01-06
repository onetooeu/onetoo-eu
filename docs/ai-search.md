# ONETOO AI Search (Homepage integration)

This repository exposes a decade-stable homepage search UI that calls the separate Search API service:

- UI host: `https://onetoo.eu/`
- Search API (recommended): `https://search.onetoo.eu/search/v1?q=...`
- Pointer entrypoint: `https://onetoo.eu/.well-known/ai-search.json`

The search API runs as a separate Cloudflare Worker (deploy from `onetoo-ai-search-v2.0`).
The onetoo.eu site remains static (TFWS trust root); the search UI is a thin client.

## CORS requirements (Search API)
Allow only:
- `https://onetoo.eu`
- `https://www.onetoo.eu`

## Verification (optional)
Search responses may include proof pointers/bundles; UI displays a proof link if present.
