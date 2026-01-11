#!/usr/bin/env bash
# ONETOO — Local verification (defrag pass)
# - deterministic checks
# - schema sanity
# - optional minisign verify if artifacts present

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# shellcheck disable=SC1091
source "$ROOT/scripts/colors.sh"

cd "$ROOT"

log "Repo: $ROOT"
log "Step 1/4 — basic hygiene"
test -f ".well-known/sha256.json" || { bad "Missing .well-known/sha256.json"; exit 1; }
test -f ".well-known/minisign.pub" || { bad "Missing .well-known/minisign.pub"; exit 1; }
ok "Required trust-root files exist"

log "Step 2/4 — validate JSON schemas (best-effort)"
if command -v python >/dev/null 2>&1; then
  python scripts/validate_schemas.py && ok "Schema validation OK" || warn "Schema validation returned non-zero (review output)"
else
  warn "python not found; skipping schema validation"
fi

log "Step 3/4 — verify minisign signatures (if present)"
if command -v minisign >/dev/null 2>&1; then
  if [ -f ".well-known/sha256.json.minisig" ]; then
    minisign -Vm ".well-known/sha256.json" -x ".well-known/sha256.json.minisig" -p ".well-known/minisign.pub"       && ok "sha256.json signature OK" || { bad "sha256.json signature FAILED"; exit 1; }
  else
    warn "No .well-known/sha256.json.minisig present — signatures not fully checkable"
  fi
else
  warn "minisign not found; skipping signature verification"
fi

log "Step 4/4 — policy parity check"
if [ -f "scripts/policy.sh" ] && [ -f ".well-known/policy.sh" ]; then
  if cmp -s "scripts/policy.sh" ".well-known/policy.sh"; then
    ok "policy.sh is identical (scripts/ == .well-known/)"
  else
    warn "policy.sh differs between scripts/ and .well-known/ (consider re-sync + re-sign)"
  fi
else
  warn "policy.sh missing in one of the locations"
fi

ok "Local verification completed"
