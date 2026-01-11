#!/usr/bin/env python3
"""Generate:
- public/_deploy.txt  (served marker)
- public/.well-known/deploy.txt (canonical trust location)
- public/.well-known/sha256.json (served inventory)
- dumps/sha256.json (legacy mirror)
- .well-known/sha256.json (root mirror, for repos that expose it)
- .well-known/deploy.txt (root mirror for tooling parity)

Design goals:
- Deterministic ordering
- No external deps
- Works in GitHub Actions (ubuntu-latest)
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

PUBLIC_DIR = REPO_ROOT / "public"
ROOT_WELLKNOWN = REPO_ROOT / ".well-known"
PUBLIC_WELLKNOWN = PUBLIC_DIR / ".well-known"
DUMPS_DIR = REPO_ROOT / "dumps"

EXCLUDE_DIRS = {".git", ".github", "node_modules", ".wrangler"}
EXCLUDE_FILES = {".DS_Store"}


def git_short_head() -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT)
        return out.decode("utf-8").strip()
    except Exception:
        return "unknown"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(p: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    size = 0
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
            size += len(chunk)
    return h.hexdigest(), size


def should_exclude(path: Path) -> bool:
    parts = set(path.parts)
    if parts & EXCLUDE_DIRS:
        return True
    if path.name in EXCLUDE_FILES:
        return True
    return False


def sync_root_wellknown_into_public() -> None:
    """Mirror root .well-known into public/.well-known so Pages output contains trust-root."""
    if not ROOT_WELLKNOWN.is_dir():
        return
    PUBLIC_WELLKNOWN.mkdir(parents=True, exist_ok=True)
    for src in ROOT_WELLKNOWN.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(ROOT_WELLKNOWN)
        dst = PUBLIC_WELLKNOWN / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def build_inventory_for_public() -> dict:
    items = []
    for f in sorted(PUBLIC_DIR.rglob("*")):
        if f.is_dir():
            continue
        if should_exclude(f):
            continue
        rel = f.relative_to(PUBLIC_DIR).as_posix()
        digest, size = sha256_file(f)
        items.append({
            "path": f"/{rel}",
            "sha256": digest,
            "bytes": size,
        })
    return {
        "schema": "onetoo:sha256-inventory:v1",
        "updated_at": utc_now(),
        "commit": git_short_head(),
        "items": items,
    }


def write_json(p: Path, data: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_deploy_marker() -> None:
    """Write deploy marker into:
    - public/_deploy.txt (optional served path)
    - public/.well-known/deploy.txt (canonical trust location)
    - .well-known/deploy.txt (repo root mirror for tooling parity)
    """
    commit = git_short_head()
    now = utc_now()

    content = (
        "DEPLOY-MARKER ROOT\n"
        f"commit: {commit}\n"
        f"time: {now}\n"
        f"nonce: cf-pages-{commit}-{now}\n"
    )

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    (PUBLIC_DIR / "_deploy.txt").write_text(content, encoding="utf-8")

    PUBLIC_WELLKNOWN.mkdir(parents=True, exist_ok=True)
    (PUBLIC_WELLKNOWN / "deploy.txt").write_text(content, encoding="utf-8")

    ROOT_WELLKNOWN.mkdir(parents=True, exist_ok=True)
    (ROOT_WELLKNOWN / "deploy.txt").write_text(content, encoding="utf-8")


def main() -> None:
    # Mini-polish: allow local runs even if public/ didn't exist yet.
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    # Ensure trust-root ends up in published output
    sync_root_wellknown_into_public()

    # Deploy marker(s)
    write_deploy_marker()

    inv = build_inventory_for_public()

    # Served canonical inventory
    write_json(PUBLIC_WELLKNOWN / "sha256.json", inv)

    # Mirrors (optional but useful for tooling parity)
    write_json(DUMPS_DIR / "sha256.json", inv)
    write_json(ROOT_WELLKNOWN / "sha256.json", inv)


if __name__ == "__main__":
    main()
