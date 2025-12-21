#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "[1/3] Regenerating sha256 inventory..."
python3 "$ROOT_DIR/scripts/generate_dumps.py"

echo "[2/3] Verifying sha256 inventory integrity (basic)..."
python3 - <<'PY'
import hashlib
from pathlib import Path
import json
root=Path(".").resolve()
inv=json.loads((root/"dumps/sha256.json").read_text("utf-8"))
files=inv["files"]
for rel, expected in files.items():
    p=root/rel
    if not p.exists():
        raise SystemExit(f"Missing: {rel}")
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    if h!=expected:
        raise SystemExit(f"Mismatch: {rel}")
print("OK")
PY

echo "[3/3] Verifying minisign signatures (if present)..."
if command -v minisign >/dev/null 2>&1 && [ -f "$ROOT_DIR/control/keys/maintainers.pub" ]; then
  for f in dumps/release.json dumps/release-mega.json dumps/sha256.json; do
    sig="dumps/sigs/$(basename "$f").minisig"
    if [ -f "$sig" ]; then
      minisign -V -p "$ROOT_DIR/control/keys/maintainers.pub" -m "$ROOT_DIR/$f" -x "$ROOT_DIR/$sig" >/dev/null
      echo "Verified: $sig"
    fi
  done
else
  echo "minisign not found or public key missing; skipping signature verification."
fi

echo "All checks passed."
