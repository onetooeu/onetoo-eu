# Architecture

Think of this repo as a **trust appliance**: a static site that can be independently verified.

## Layers

### 1) Identity layer
- `/.well-known/ai-trust-hub.json`
- `/.well-known/minisign.pub`

### 2) Integrity layer
- `/dumps/sha256.json` (complete file inventory)
- `/dumps/sigs/*.minisig` (signatures)

### 3) Change layer
- `/changelog/` (what changed)
- `/incidents/` (what went wrong)

### 4) API layer
- `/openapi.json`
- `/api/v1/*` (optional endpoints)

## Determinism
- Hash inventory is generated in stable ordering (POSIX paths).
- Self-generated dump targets are excluded.

## Conventions
- `.well-known/*` is for automation discovery.
- `control/` is operator-maintained assets (keys, inbox, internal templates).
- `schemas/` defines JSON contracts used across the hub.
