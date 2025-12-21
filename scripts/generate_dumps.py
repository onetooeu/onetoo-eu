#!/usr/bin/env python3
"""Regenerate dumps/sha256.{json,txt} deterministically.

Design goals:
- Deterministic ordering (stable across platforms)
- No self-references (exclude the dump files themselves)
- CI-friendly metadata (timestamp, git commit)

Usage:
  python3 scripts/generate_dumps.py
  python3 scripts/generate_dumps.py --ci
  python3 scripts/generate_dumps.py --generated-at 2025-12-19T18:00:00Z

Notes:
- By default, we hash *everything* that ships to Cloudflare Pages.
- Exclusions are only for self-generated dump targets (and .git).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
DUMPS_DIR = ROOT / "dumps"

EXCLUDE_FILES = {
    DUMPS_DIR / "sha256.json",
    DUMPS_DIR / "sha256.txt",
}

EXCLUDE_DIR_NAMES = {".git"}

@dataclass(frozen=True)
class FileHash:
    rel: str
    sha256: str


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def try_git(cmd: List[str]) -> str:
    try:
        out = subprocess.check_output(cmd, cwd=ROOT, stderr=subprocess.DEVNULL)
        return out.decode("utf-8").strip()
    except Exception:
        return ""


def iter_files() -> List[Path]:
    out: List[Path] = []
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if any(part in EXCLUDE_DIR_NAMES for part in p.parts):
            continue
        if p in EXCLUDE_FILES:
            continue
        out.append(p)
    return out


def build_hashes() -> List[FileHash]:
    files = iter_files()
    # stable ordering: POSIX relative path
    rels: List[Tuple[str, Path]] = [(p.relative_to(ROOT).as_posix(), p) for p in files]
    rels.sort(key=lambda x: x[0])
    return [FileHash(rel=rel, sha256=sha256_file(p)) for rel, p in rels]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--generated-at", default="", help="RFC3339 timestamp (e.g. 2025-12-19T18:00:00Z)")
    ap.add_argument("--ci", action="store_true", help="Fill metadata from CI env vars when possible")
    args = ap.parse_args()

    hashes = build_hashes()
    files_map: Dict[str, str] = {h.rel: h.sha256 for h in hashes}

    generated_at = args.generated_at
    if args.ci and not generated_at:
        # Prefer GitHub Actions timestamp if available; otherwise keep stable placeholder.
        generated_at = os.environ.get("GITHUB_RUN_ID", "")
        # If we only get a run id, store as a marker; caller can replace with an ISO timestamp if desired.
        if generated_at:
            generated_at = f"gha-run:{generated_at}"

    if not generated_at:
        generated_at = "REPLACE_IN_CI"

    commit = try_git(["git", "rev-parse", "HEAD"]) or ""
    dirty = "" if not commit else ("dirty" if try_git(["git", "status", "--porcelain"]) else "clean")

    out_json = {
        "$schema": "/schemas/dumps-sha256.schema.json",
        "platform": "cloudflare-pages",
        "operator": "onetoo.eu",
        "generated_at": generated_at,
        "algorithm": "sha256",
        "git": {
            "commit": commit,
            "working_tree": dirty,
        },
        "count": len(files_map),
        "files": files_map,
    }

    DUMPS_DIR.mkdir(exist_ok=True)
    (DUMPS_DIR / "sha256.json").write_text(
        json.dumps(out_json, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (DUMPS_DIR / "sha256.txt").write_text(
        "".join(f"{sha}  {rel}\n" for rel, sha in files_map.items()),
        encoding="utf-8",
    )
    print(f"Wrote {len(files_map)} hashes.")


if __name__ == "__main__":
    main()
