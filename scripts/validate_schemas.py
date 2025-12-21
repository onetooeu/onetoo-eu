#!/usr/bin/env python3
"""Validate core machine-readable artifacts against JSON Schemas.

This keeps ONETOO Trust Hub machine endpoints predictable and safe for agents.

Exit non-zero on validation errors.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    try:
        from jsonschema import Draft202012Validator
    except Exception as e:
        print("Missing dependency: jsonschema. Install via `pip install jsonschema`.", file=sys.stderr)
        print(str(e), file=sys.stderr)
        return 2

    root = Path(__file__).resolve().parents[1]

    targets = [
        (root / ".well-known" / "ai-trust-hub.json", root / "schemas" / "ai-trust-hub.schema.json"),
        (root / ".well-known" / "sigstore.json", root / "schemas" / "sigstore-meta.schema.json"),
        (root / "dumps" / "sha256.json", root / "schemas" / "sha256-inventory.schema.json"),
        (root / "dumps" / "release.json", root / "schemas" / "release.schema.json"),
        (root / "dumps" / "release-mega.json", root / "schemas" / "release.schema.json"),
        (root / "dumps" / "attestations" / "index.json", root / "schemas" / "sigstore-attestations.schema.json"),
        (root / "incidents" / "index.json", root / "schemas" / "incidents-index.schema.json"),
    ]

    ok = True
    for data_path, schema_path in targets:
        if not data_path.exists():
            print(f"SKIP: {data_path.relative_to(root)} (missing)")
            continue
        if not schema_path.exists():
            print(f"ERROR: schema missing: {schema_path.relative_to(root)}", file=sys.stderr)
            ok = False
            continue

        data = load_json(data_path)
        schema = load_json(schema_path)
        v = Draft202012Validator(schema)
        errors = sorted(v.iter_errors(data), key=lambda e: list(e.absolute_path))
        if errors:
            ok = False
            print(f"\n❌ INVALID: {data_path.relative_to(root)}")
            for err in errors[:20]:
                path = "/".join([str(p) for p in err.absolute_path])
                print(f"  - at {path or '/'}: {err.message}")
        else:
            print(f"✅ VALID: {data_path.relative_to(root)}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
