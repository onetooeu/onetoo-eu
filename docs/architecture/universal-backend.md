# Universal Backend (Worker/API) – Architecture Note

## Why this exists
`search.onetoo.eu` returned 404 because there was **no runtime** deployed.
The trust-root remains valid without it, but for **ecosystem completeness** we provide
a **small universal backend** that:

- gives AI agents a stable API entry point
- exposes OpenAPI (`/openapi.json`)
- provides healthcheck (`/health`)
- offers a deterministic placeholder for search (`/search/v1`)
- proxies canonical trust-root artifacts (`/trust/v1/*`) from `www.onetoo.eu`

## Security posture
- No secrets required for the base version.
- No write endpoints.
- Proxies only a tiny allowlist (`deploy.txt`, `sha256.json`).

## Upgrade path (later)
- Add real indexing/search (KV/D1/R2)
- Add maintainer-only endpoints (secrets via `wrangler secret put`)
- Split into microservices if needed
