#!/usr/bin/env python3
"""ONETOO Autopilot (Bot Mode)

This script is intentionally conservative:
- deterministic output
- fail-closed
- only touches allow-listed outputs

Default behavior in this template:
- canonicalizes JSON dumps (stable formatting)
- optionally sorts .items by stable keys when obvious

Hook your real pipeline (pending->sandbox->accepted) in `apply_domain_rules()`.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from lib.guard import fail, require_repo_root
from lib.jsoncanon import dump_canonical_json


@dataclass(frozen=True)
class Config:
    repo_root: Path
    allowlist: List[str]
    sort_item_keys: Tuple[str, ...]
    max_items: int


def load_config(repo_root: Path) -> Config:
    cfg_path = repo_root / "tools" / "autopilot" / "config.json"
    if not cfg_path.exists():
        fail(f"Missing config: {cfg_path}")

    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

    allowlist = list(cfg.get("allowlist", []))
    if not allowlist:
        fail("Config.allowlist must not be empty")

    sort_keys = cfg.get("rules", {}).get("sort_items_by", ["id", "domain", "url"])
    max_items = int(cfg.get("rules", {}).get("max_items", 200000))

    return Config(
        repo_root=repo_root,
        allowlist=allowlist,
        sort_item_keys=tuple(sort_keys),
        max_items=max_items,
    )


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"JSON parse failed: {path} :: {e}")


def maybe_sort_items(obj: Any, sort_keys: Tuple[str, ...], max_items: int, src: Path) -> Any:
    """If obj looks like {items:[...]}, sort items deterministically.

    Sorting strategy:
    - If item is dict and contains any of sort_keys, use first existing as primary.
    - Otherwise keep original order.

    This is intentionally conservative to avoid changing semantics.
    """

    if not isinstance(obj, dict):
        return obj
    items = obj.get("items")
    if not isinstance(items, list):
        return obj

    if len(items) > max_items:
        fail(f"Refusing to process {src}: items length {len(items)} exceeds max_items={max_items}")

    # Determine a stable key function.
    def key_fn(x: Any):
        if isinstance(x, dict):
            for k in sort_keys:
                v = x.get(k)
                if isinstance(v, str):
                    return (k, v)
        return ("", "")

    # Only sort if it *actually* gives a deterministic, meaningful order:
    # at least one element must have a usable key.
    if any(isinstance(i, dict) and any(isinstance(i.get(k), str) for k in sort_keys) for i in items):
        obj = dict(obj)
        obj["items"] = sorted(items, key=key_fn)
    return obj


def apply_domain_rules(repo_root: Path, cfg: Config) -> None:
    """PLACEHOLDER for real autopilot logic.

    In your production version, this function should:
      - load pending submissions
      - compute sandbox/accepted updates deterministically
      - update ledgers
      - write results via atomic writes

    In this template, we only canonicalize allow-listed JSON files.
    """

    for rel in cfg.allowlist:
        # JSONL is allowed in allowlist, but this template only canonicalizes JSON.
        if rel.endswith(".jsonl"):
            continue

        p = repo_root / rel
        if not p.exists():
            # Fail-closed: if a target is missing, we abort (prevents accidental partial updates).
            fail(f"Missing allow-listed target: {rel}")

        data = read_json(p)
        data = maybe_sort_items(data, cfg.sort_item_keys, cfg.max_items, p)

        before = p.read_text(encoding="utf-8")
        dump_canonical_json(p, data, sort_keys=True, compact=True, ensure_ascii=False, newline=True)
        after = p.read_text(encoding="utf-8")
        if after != before:
            print(f"[autopilot] canonicalized: {rel}")

def main() -> int:
    repo_root = require_repo_root(Path(os.environ.get("ONETOO_REPO_ROOT", ".")).resolve())
    cfg = load_config(repo_root)

    # Hard rule: never run outside GitHub Actions unless explicitly allowed.
    # (You can disable this locally by exporting ONETOO_MODE=local)
    mode = os.environ.get("ONETOO_MODE", "").strip().lower()
    if mode not in {"ci", "local"}:
        fail("Set ONETOO_MODE=ci (in Actions) or ONETOO_MODE=local (manual run)")

    apply_domain_rules(repo_root, cfg)

    # Optional: write a minimal log line (JSONL) only if file exists.
    log_path = repo_root / "public" / "dumps" / "autopilot-log.jsonl"
    if log_path.exists():
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        log_path.write_text(log_path.read_text(encoding="utf-8") + json.dumps({"ts": now, "ok": True}) + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
