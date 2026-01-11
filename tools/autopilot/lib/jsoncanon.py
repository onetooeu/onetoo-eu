from __future__ import annotations

import json
from pathlib import Path
from typing import Any

def dump_canonical_json(
    path: Path,
    obj: Any,
    *,
    sort_keys: bool = True,
    compact: bool = True,
    ensure_ascii: bool = False,
    newline: bool = True,
) -> None:
    # Deterministic JSON dump for stable diffs.
    if compact:
        text = json.dumps(
            obj,
            ensure_ascii=ensure_ascii,
            sort_keys=sort_keys,
            separators=(",", ":"),
        )
    else:
        text = json.dumps(
            obj,
            ensure_ascii=ensure_ascii,
            sort_keys=sort_keys,
            indent=2,
        )

    if newline and not text.endswith("\n"):
        text += "\n"

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
