#!/usr/bin/env bash
set -euo pipefail

# Local dev helper for ONETOO Universal Worker
# Usage: scripts/local/dev-universal-worker.sh

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WORKER_DIR="$ROOT/worker/onetoo-universal"

if ! command -v wrangler >/dev/null 2>&1; then
  echo "wrangler not found. Install: npm i -g wrangler" >&2
  exit 1
fi

cd "$WORKER_DIR"
echo "[dev] cwd: $WORKER_DIR"
echo "[dev] starting wrangler dev ..."
wrangler dev
