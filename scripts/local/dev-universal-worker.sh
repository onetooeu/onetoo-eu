#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../worker/onetoo-universal"
echo "== dev: onetoo-universal =="
wrangler dev
