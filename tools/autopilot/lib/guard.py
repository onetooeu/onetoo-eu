from __future__ import annotations

import os
from pathlib import Path

def fail(msg: str) -> None:
    raise SystemExit(f"[autopilot][FAIL] {msg}")

def require_repo_root(p: Path | None = None) -> Path:
    if p is None:
        root = os.environ.get("GITHUB_WORKSPACE") or os.environ.get("ONETOO_REPO_ROOT")
        if not root:
            fail("Missing ONETOO_REPO_ROOT or GITHUB_WORKSPACE")
        p = Path(root).resolve()
    else:
        p = Path(p).resolve()

    if not (p / ".git").exists():
        fail(f"Not a git repository: {p}")
    return p
