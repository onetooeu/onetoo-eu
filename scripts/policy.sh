#!/usr/bin/env bash
# ONETOO / TFWS deterministic policy helper (reference implementation)
# Purpose: provide a single, auditable place for "hard-fail" and "soft-score" rules
# used by tooling (e.g., autopilot) and by humans during review.
#
# NOTE: This script is designed to be:
# - deterministic (same input -> same output)
# - side-effect free (no network calls by default)
# - portable (bash, coreutils)
#
# INPUT:  a JSON file describing a submission (minimal schema below), OR "-" for stdin.
# OUTPUT: a JSON decision object on stdout.
#
# Minimal input schema:
# {
#   "url": "https://example.com",
#   "id":  "sha256-of-canonical-record-or-other-stable-id",
#   "declared": { ... optional ... }
# }
#
# Decision output schema:
# {
#   "id": "...",
#   "ok": true|false,
#   "hard_fail": [ {"code":"...", "msg":"..."} ],
#   "score": 0..100,
#   "signals": [ {"code":"...", "weight":..., "msg":"..."} ],
#   "ts": "YYYY-MM-DDTHH:MM:SSZ"
# }
set -euo pipefail

in="${1:--}"

read_input() {
  if [ "$in" = "-" ]; then
    cat
  else
    cat "$in"
  fi
}

# tiny json getter (no jq required). For full fidelity, prefer jq.
json_get() {
  # usage: json_get key
  python3 - "$1" <<'PY'
import json,sys
key=sys.argv[1]
obj=json.load(sys.stdin)
print(obj.get(key,""))
PY
}

payload="$(read_input)"
url="$(printf "%s" "$payload" | json_get url)"
id="$(printf "%s" "$payload" | json_get id)"

hard_fail=()
signals=()
score=50

add_hard_fail(){ hard_fail+=("$1|$2"); }
add_signal(){ signals+=("$1|$2|$3"); score=$((score + $2)); }

# ---- HARD FAILS ----
if [ -z "$url" ]; then
  add_hard_fail "NO_URL" "Missing 'url' field"
else
  case "$url" in
    https://*) : ;;
    *) add_hard_fail "NON_HTTPS" "URL must be HTTPS" ;;
  esac

  # forbid obvious localhost / private nets (defense-in-depth)
  case "$url" in
    *://localhost/*|*://127.*/*|*://10.*/*|*://192.168.*/*|*://172.1[6-9].*/*|*://172.2[0-9].*/*|*://172.3[0-1].*/*)
      add_hard_fail "PRIVATE_NET" "Private/localhost targets are not allowed"
    ;;
  esac
fi

# ---- SOFT SIGNALS ----
if [ -n "$url" ]; then
  case "$url" in
    https://www.*) add_signal "HAS_WWW" 1 "Has www subdomain" ;;
  esac
  case "$url" in
    *.onion/*) add_hard_fail "ONION" "Onion/Tor URLs are not accepted in public registry" ;;
  esac
fi

# clamp score
if [ "$score" -lt 0 ]; then score=0; fi
if [ "$score" -gt 100 ]; then score=100; fi

ok=true
if [ "${#hard_fail[@]}" -gt 0 ]; then ok=false; fi

ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

python3 - <<PY
import json,sys
id_=${json.dumps(id)}
hard=${json.dumps(hard_fail)}
sig=${json.dumps(signals)}
def split2(x):
  code,msg=x.split("|",1)
  return {"code":code,"msg":msg}
def split3(x):
  code,w,msg=x.split("|",2)
  return {"code":code,"weight":int(w),"msg":msg}
out={
  "id": id or None,
  "ok": ${str(ok).lower()},
  "hard_fail": [split2(x) for x in hard] if hard else [],
  "score": ${score},
  "signals": [split3(x) for x in sig] if sig else [],
  "ts": "${ts}"
}
print(json.dumps(out, ensure_ascii=False, separators=(",",":")) + "\n")
PY
