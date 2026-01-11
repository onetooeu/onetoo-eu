#!/usr/bin/env python3
"""Stage allow-listed outputs only.

This script is called by the workflow before commit.
It prevents accidental 'git add .' and fails closed if
anything outside allowlist is modified.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import List

from lib.guard import fail, require_repo_root


def sh(cmd: List[str]) -> str:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        fail(f"Command failed ({' '.join(cmd)}): {p.stderr.strip()}")
    return p.stdout


def load_allowlist(repo_root: Path) -> List[str]:
    cfg_path = repo_root / "tools" / "autopilot" / "config.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    allow = cfg.get("allowlist", [])
    if not allow:
        fail("config.json allowlist is empty")
    return list(allow)


def main() -> int:
    repo_root = require_repo_root()
    allowlist = set(load_allowlist(repo_root))

    # Detect working-tree changes (including unstaged)
    porcelain = sh(["git", "status", "--porcelain"])
    changed_paths = []
    for line in porcelain.splitlines():
        if not line:
            continue
        # Format: XY <path>
        path = line[3:].strip()
        if path:
            changed_paths.append(path)

    # Fail closed if anything changed outside allowlist.
    outside = sorted({p for p in changed_paths if p not in allowlist})
    if outside:
        fail(
            "Refusing to stage because non-allowlisted paths changed:\n"
            + "\n".join(f"  - {p}" for p in outside)
        )

    # Stage allow-listed paths that exist.
    for rel in sorted(allowlist):
        p = repo_root / rel
        if p.exists():
            sh(["git", "add", rel])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
