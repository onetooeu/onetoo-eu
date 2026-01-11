#!/usr/bin/env bash
set -euo pipefail

# ONETOO re-audit (read-only)
# - checks deploy marker + sha256 inventory on both domains
# - checks search.onetoo.eu basic reachability (expected 404 today)

cb() { date +%s; }

fetch() {
  local url="$1"
  curl -sS "$url"
}

headn() { sed -n "1,${1}p"; }

echo "=== (1) deploy markers ==="
for host in "https://onetoo-eu.pages.dev" "https://www.onetoo.eu"; do
  echo "--- $host/.well-known/deploy.txt"
  fetch "$host/.well-known/deploy.txt?cb=$(cb)" | headn 6
done

echo
echo "=== (2) sha256.json (commit line) ==="
for host in "https://onetoo-eu.pages.dev" "https://www.onetoo.eu"; do
  echo "--- $host/.well-known/sha256.json"
  fetch "$host/.well-known/sha256.json?cb=$(cb)" | grep -n '"commit"' | head -n 1 || true
done

echo
echo "=== (3) headers (cache hints) ==="
for host in "https://onetoo-eu.pages.dev" "https://www.onetoo.eu"; do
  echo "--- HEAD $host/.well-known/sha256.json"
  curl -sSI "$host/.well-known/sha256.json?cb=$(cb)" | egrep -i "HTTP/|cf-cache-status|cache-control|etag|last-modified|age|content-type" || true
done

echo
echo "=== (4) search.onetoo.eu check (expected 404) ==="
# We do not assume any specific endpoint exists; we probe a few common ones.
for path in "/" "/health" "/openapi.json" "/.well-known/ai-search.json"; do
  url="https://search.onetoo.eu${path}"
  code="$(curl -sS -o /dev/null -w "%{http_code}" "$url?cb=$(cb)" || true)"
  echo "$url -> HTTP $code"
done

echo
echo "OK: re-audit script finished."
