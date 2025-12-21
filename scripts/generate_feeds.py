#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

BASE_URL = "https://onetoo.eu"  # canonical public base


def utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def to_updated_iso(ts_any) -> str:
    # Use generated_at if present; else now.
    if isinstance(ts_any, str) and ts_any.strip():
        return ts_any
    return utc_now_iso()


def write_atom(
    feed_path: Path,
    *,
    feed_id: str,
    title: str,
    self_href: str,
    home_href: str,
    items: list[dict],
    generated_at: str,
    item_kind: str,
) -> None:
    updated = to_updated_iso(generated_at)

    entries_xml: list[str] = []
    for it in (items or [])[:50]:
        it_id = it.get("id") or it.get("href") or "item"
        href = it.get("href") or ""
        item_url = (BASE_URL + href) if href.startswith("/") else href
        item_title = it.get("title") or it.get("name") or str(it_id)

        it_date = it.get("date") or it.get("updated_at") or it.get("created_at") or updated

        if item_kind == "incidents":
            st = it.get("status") or it.get("severity") or ""
            summary = f"Incident update: {item_title}" + (f" ({st})" if st else "")
        else:
            summary = f"Changelog entry: {item_title}"

        entries_xml.append(
            f"""
  <entry>
    <id>{escape(str(feed_id) + ":" + str(it_id))}</id>
    <title>{escape(str(item_title))}</title>
    <updated>{escape(str(it_date))}</updated>
    <link rel="alternate" href="{escape(item_url)}"/>
    <summary>{escape(summary)}</summary>
  </entry>""".rstrip()
        )

    if not entries_xml:
        entries_xml.append(
            f"""
  <entry>
    <id>{escape(feed_id + ":empty")}</id>
    <title>No entries</title>
    <updated>{escape(updated)}</updated>
    <summary>Empty feed</summary>
  </entry>""".rstrip()
        )

    atom = f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <id>{escape(feed_id)}</id>
  <title>{escape(title)}</title>
  <updated>{escape(updated)}</updated>
  <link rel="self" href="{escape(BASE_URL + self_href)}"/>
  <link rel="alternate" href="{escape(BASE_URL + home_href)}"/>
{chr(10).join(entries_xml)}
</feed>
"""

    feed_path.parent.mkdir(parents=True, exist_ok=True)
    feed_path.write_text(atom, encoding="utf-8")


def main() -> None:
    root = Path(".")
    now = utc_now_iso()

    # Changelog
    c = json.loads((root / "changelog/index.json").read_text(encoding="utf-8"))
    c_items = c.get("entries", []) if isinstance(c.get("entries"), list) else []
    c_gen = c.get("generated_at", now)
    write_atom(
        root / "changelog/feed.xml",
        feed_id=f"{BASE_URL}/changelog/feed.xml",
        title="ONETOO Changelog (Atom)",
        self_href="/changelog/feed.xml",
        home_href="/changelog/",
        items=c_items,
        generated_at=c_gen,
        item_kind="changelog",
    )

    # Incidents
    i = json.loads((root / "incidents/index.json").read_text(encoding="utf-8"))
    i_items = i.get("items", []) if isinstance(i.get("items"), list) else []
    i_gen = i.get("generated_at", now)
    write_atom(
        root / "incidents/feed.xml",
        feed_id=f"{BASE_URL}/incidents/feed.xml",
        title="ONETOO Incidents (Atom)",
        self_href="/incidents/feed.xml",
        home_href="/incidents/",
        items=i_items,
        generated_at=i_gen,
        item_kind="incidents",
    )

    print("Generated changelog/feed.xml and incidents/feed.xml ✅")


if __name__ == "__main__":
    main()
