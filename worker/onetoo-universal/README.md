# ONETOO Universal Backend (Cloudflare Worker)

**Worker name:** `onetoo-universal`  
**Purpose:** stable API runtime for `search.onetoo.eu` that avoids 404 and provides a deterministic, minimal endpoint surface.

## Goals (Phase 2)
- Remove 404 on `https://search.onetoo.eu/*`
- Provide stable endpoints:
  - `GET /` (info)
  - `GET /health`
  - `GET /openapi.json`
  - `GET /search/v1` (placeholder; returns 501 until index is enabled)
  - `GET /trust/v1/deploy` (proxy `/.well-known/deploy.txt` from trust-root)
  - `GET /trust/v1/sha256` (proxy `/.well-known/sha256.json` from trust-root)
- Keep trust-root **sealed**; backend is an adapter layer.

## Quickstart (local)
```bash
cd worker/onetoo-universal
cp -f wrangler.toml.example wrangler.toml
# edit wrangler.toml: set account_id; (optionally) enable routes
wrangler dev
```

## Deploy
```bash
cd worker/onetoo-universal
wrangler deploy
```

If routes are enabled in `wrangler.toml`, the deploy will also attach:
- `search.onetoo.eu/*` (zone: `onetoo.eu`)

## Expected behavior
- `/health` → **200**
- `/openapi.json` → **200**
- `/search/v1?q=test` → **501** with a controlled JSON body
- `/trust/v1/deploy` → **200** plaintext proxy
- `/trust/v1/sha256` → **200** JSON proxy

## Security notes
- No secrets are stored in repo.
- Worker returns `Cache-Control: no-store` for all responses.
- Default CORS is permissive for GET-only usage; can be tightened later.

## License
Inherit repository license.
