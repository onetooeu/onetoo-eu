from __future__ import annotations

from typing import Any, Dict, List


def _sort_items(items: List[Dict[str, Any]], keys: List[str]) -> List[Dict[str, Any]]:
    def k(it: Dict[str, Any]):
        for key in keys:
            if key in it and isinstance(it[key], str):
                return (key, it[key])
        # fallback: stable string of dict keys
        return ("__fallback__", str(sorted(it.keys())))

    return sorted(items, key=k)


def normalize_registry(obj: Any, *, sort_items_by: List[str], max_items: int) -> Any:
    """Best-effort deterministic normalization.

    Works with common ONETOO-style shapes:
      - {"items": [...]} where items are dicts
      - lists of dicts

    If shape is unknown, returns input unchanged.
    """
    if isinstance(obj, dict) and isinstance(obj.get("items"), list):
        items = obj["items"]
        if len(items) > max_items:
            raise ValueError(f"items too large: {len(items)} > {max_items}")
        if all(isinstance(x, dict) for x in items):
            obj = dict(obj)
            obj["items"] = _sort_items(items, sort_items_by)
            return obj
        return obj

    if isinstance(obj, list):
        if len(obj) > max_items:
            raise ValueError(f"list too large: {len(obj)} > {max_items}")
        if all(isinstance(x, dict) for x in obj):
            return _sort_items(obj, sort_items_by)
        return obj

    return obj
