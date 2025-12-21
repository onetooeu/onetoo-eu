# ONETOO.eu — AI Trust Hub

This repository is a **static, audit-friendly trust & governance hub** designed for:
- AI agents (machine-readable trust manifest + OpenAPI)
- partners/auditors (verification, integrity inventory, incident/changelog rails)
- humans (clear landing pages)

## What this ships

**Human entrypoints**
- `/` (index)
- `/ai-trust-hub.html`
- `/verify.html`

**Machine entrypoints**
- `/.well-known/ai-trust-hub.json`
- `/.well-known/llms.txt`
- `/.well-known/minisign.pub`
- `/dumps/sha256.json` + `/dumps/sigs/*.minisig`

## Golden rules (the “Mozart mode”)

1. **Everything that matters is linkable** (stable URLs, no hidden knowledge).
2. **Everything that ships is hashable** (`dumps/sha256.json`).
3. **Everything that’s hashable is signable** (minisign signatures in CI).
4. **Everything is machine-readable first** (JSON/OpenAPI), and human-friendly second.

## Local workflow

```bash
python3 scripts/generate_dumps.py
bash scripts/verify_local.sh
```

## CI signing

See `docs/CI-SIGNING.md`.
