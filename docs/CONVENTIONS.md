# Conventions

## File structure
- `/.well-known/` discovery endpoints
- `/dumps/` integrity inventory + signatures
- `/schemas/` JSON schemas
- `/scripts/` maintenance scripts
- `/docs/` documentation

## Naming
- Prefer kebab-case for directories and filenames.
- Prefer stable URLs (avoid renames that break external verifiers).

## JSON discipline
- All `*.json` must be valid JSON (CI enforces it).
- Add `$schema` pointers where applicable.
