# ONETOO Universal Backend (Cloudflare Worker)

This Worker is the **missing runtime layer** for the ONETOO ecosystem.
It is designed to make `https://search.onetoo.eu` respond **deterministically**
(without breaking the "publish & forget" trust-root).

## Goals
- Provide a stable **/health** endpoint (always 200 when deployed)
- Provide **/openapi.json** (machine-readable contract)
- Provide **/search/v1** as a **stable, explicit** API surface:
  - today: returns 501 with a clear message (until search index exists)
  - later: can be extended to real search
- Provide **/trust/v1/** utilities that help agents:
  - fetch and verify canonical trust-root data from `www.onetoo.eu/.well-known/*`

## Non-goals (by design)
- This does NOT change the trust-root content or signing model.
- This does NOT require secrets to be committed (use `wrangler secret put`).

## Deploy overview (short)
1. Install wrangler: `npm i -g wrangler`
2. Login: `wrangler login`
3. Copy config: `cp wrangler.toml.example wrangler.toml` and fill `account_id`.
4. Deploy: `wrangler deploy`

See `APPLY_UNIVERSAL_WORKER_v1.txt` in the patch zip for a step-by-step procedure.
