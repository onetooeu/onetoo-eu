#!/usr/bin/env bash
# ONETOO — Remote verification (defrag pass)
# Usage: bash scripts/verify_remote.sh https://www.onetoo.eu

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# shellcheck disable=SC1091
source "$ROOT/scripts/colors.sh"

BASE="${1:-}"
if [ -z "$BASE" ]; then
  bad "Missing BASE URL. Example: bash scripts/verify_remote.sh https://www.onetoo.eu"
  exit 2
fi

need(){ command -v "$1" >/dev/null 2>&1 || { bad "Missing dependency: $1"; exit 3; }; }

need curl
need sha256sum

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

log "Target: $BASE"
log "Temp:   $TMP"

fetch(){
  local url="$1" out="$2"
  curl -fsSL "$url" -o "$out"
}

log "Step 1/3 — fetch trust-root artifacts"
fetch "$BASE/.well-known/minisign.pub" "$TMP/minisign.pub"
fetch "$BASE/.well-known/sha256.json" "$TMP/sha256.json"
ok "Fetched minisign.pub + sha256.json"

if curl -fsSL "$BASE/.well-known/sha256.json.minisig" -o "$TMP/sha256.json.minisig" >/dev/null 2>&1; then
  ok "Fetched sha256.json.minisig"
else
  warn "sha256.json.minisig not available (remote signatures may be incomplete)"
fi

log "Step 2/3 — verify signature (optional)"
if command -v minisign >/dev/null 2>&1 && [ -f "$TMP/sha256.json.minisig" ]; then
  minisign -Vm "$TMP/sha256.json" -x "$TMP/sha256.json.minisig" -p "$TMP/minisign.pub"     && ok "Remote sha256.json signature OK" || { bad "Remote sha256.json signature FAILED"; exit 4; }
else
  warn "minisign missing or signature not present; skipping minisign verify"
fi

log "Step 3/3 — spot-check a few files from sha256.json (best-effort)"
# Try to parse a few entries without jq (portable): look for "path" + "sha256".
python_spotcheck(){
  python - <<'PY'
import json, os, sys, random, re, subprocess, pathlib, urllib.request

base=os.environ["BASE"]
tmp=os.environ["TMP"]
with open(os.path.join(tmp,"sha256.json"),"r",encoding="utf-8") as f:
    data=json.load(f)

items = data.get("items") or data.get("files") or []
# Normalize: [{path, sha256}] expected
norm=[]
for it in items:
    p = it.get("path") or it.get("file") or it.get("name")
    h = it.get("sha256") or it.get("hash")
    if p and h and isinstance(p,str) and isinstance(h,str):
        norm.append((p.lstrip("/"), h.lower()))
random.shuffle(norm)
pick = norm[:8] if len(norm)>=8 else norm
print(f"[i] found {len(norm)} hash entries; checking {len(pick)}")
ok=0
for p,h in pick:
    url=f"{base}/{p}"
    out=os.path.join(tmp, "f_" + re.sub(r'[^a-zA-Z0-9._-]+','_',p))
    try:
        urllib.request.urlretrieve(url, out)
    except Exception as e:
        print(f"[!!] fetch failed: {p} -> {e}")
        continue
    got=subprocess.check_output(["sha256sum", out], text=True).split()[0].lower()
    if got==h:
        print(f"[OK] {p}")
        ok+=1
    else:
        print(f"[XX] {p} mismatch")
print(f"[i] ok {ok}/{len(pick)}")
PY
}
if command -v python >/dev/null 2>&1; then
  BASE="$BASE" TMP="$TMP" python_spotcheck && ok "Spot-check complete" || warn "Spot-check had issues"
else
  warn "python not found; skipping spot-check"
fi

ok "Remote verification completed"
