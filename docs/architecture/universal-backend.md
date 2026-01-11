# Universal Backend (Cloudflare Worker) — Architecture

**Component:** `worker/onetoo-universal`  
**Domain / Route:** `search.onetoo.eu/*`  
**Status:** Phase 2 complete (deployment + routing + sanity endpoints)

## Why this exists
ONETOO trust-root (`www.onetoo.eu`) is a static, sealed source-of-truth.
The `search.onetoo.eu` subdomain is intended to host dynamic services (search, policy, routing).
Without a Worker route, `search.onetoo.eu` returns Cloudflare default 404.

This Worker provides:
- a stable runtime surface (no 404s)
- deterministic placeholder behavior for not-yet-enabled services
- proxy helpers to trust-root artifacts

## Design principles
- **Trust-root stays sealed**: Worker never mutates trust-root, only reads.
- **Deterministic responses**: stable JSON, stable status codes.
- **No secrets in repo**: only non-sensitive configuration.
- **No-store**: API responses are marked `Cache-Control: no-store`.
- **CORS minimal**: GET + OPTIONS only.

## Endpoints
- `GET /`  
  Info JSON so the root path is not ambiguous.
- `GET /health`  
  Minimal healthcheck.
- `GET /openapi.json`  
  Self-describing API contract.
- `GET /search/v1?q=`  
  Placeholder returning 501 with controlled JSON until index is enabled.
- `GET /trust/v1/deploy`  
  Proxies `https://www.onetoo.eu/.well-known/deploy.txt`
- `GET /trust/v1/sha256`  
  Proxies `https://www.onetoo.eu/.well-known/sha256.json`

## Deployment notes
- The canonical route is declared in `wrangler.toml` via:
  ```toml
  routes = [
    { pattern = "search.onetoo.eu/*", zone_name = "onetoo.eu" }
  ]
  ```
- Deploy:
  ```bash
  cd worker/onetoo-universal
  wrangler deploy
  ```

## Sanity checklist
- `curl -i https://search.onetoo.eu/health` → 200
- `curl -i https://search.onetoo.eu/openapi.json` → 200
- `curl -i "https://search.onetoo.eu/search/v1?q=test"` → 501
- `curl -i https://search.onetoo.eu/trust/v1/deploy` → 200 (text)
- `curl -i https://search.onetoo.eu/trust/v1/sha256` → 200 (json)

## Next phases (not included here)
- Phase 3A: real search index (KV/D1/Vectorize)
- Phase 3B: policy engine + trust routing
- Phase 3C: public adoption docs
- Phase 3D: freeze/seal of runtime surface
