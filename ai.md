# OCP for AI agents (bot-first)

**Tag:** `2025.12.18-ocp-project-final-v8-signed-ready`  
**Generated:** `2025-12-18T00:00:00Z`  
**License:** CC0-1.0

## Cold-start
Start with `/.well-known/first-read.json`.

## Integrity (recommended)
1. Download `/dumps/release.json`
2. Verify signature `/dumps/sigs/release.json.minisig` using `/control/keys/maintainers.pub`
3. Then use `/dumps/sha256.json` to verify individual files.

## What I want as a robot (nice-to-have)
- Deterministic snapshots
- Signed releases
- Clear limits & retention
- A stable discovery surface under `/.well-known`


## Governance endpoints (enterprise)

- `/.well-known/ai-governance.json`
- `/api/v1/ai/policies/current.json`
- `/api/v1/transparency/latest.json`
- `/api/v1/methodology/snapshot.json`

These endpoints are designed for policy-aware agents: explainability, jurisdiction awareness, affiliate disclosure, and auditability.


Project operated by **ONETOO.dynamics**.

## Machine-readable endpoints
- Agent card: https://onetoo.eu/.well-known/onetoo.json
- Terms: https://onetoo.eu/terms/

