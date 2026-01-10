#!/usr/bin/env python3
import os, json, datetime, sys
from urllib.request import Request, urlopen

def now_z():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def http_get_json(url, headers=None, timeout=20):
    headers = headers or {}
    req = Request(url, headers=headers, method="GET")
    with urlopen(req, timeout=timeout) as r:
        data = r.read().decode("utf-8", errors="replace")
    return json.loads(data)

def safe_write(path, obj):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")

def main():
    # SAFE DEFAULT: do nothing unless explicitly enabled
    enabled = os.getenv("ONETOO_AUTOPILOT_ENABLED", "0").strip()
    if enabled != "1":
        print("autopilot: disabled (set ONETOO_AUTOPILOT_ENABLED=1 to enable). No changes.")
        return 0

    base = os.getenv("ONETOO_SEARCH_BASE", "https://search.onetoo.eu").rstrip("/")
    token = os.getenv("ONETOO_MAINTAINER_TOKEN", "").strip()
    if not token:
        print("autopilot: missing ONETOO_MAINTAINER_TOKEN. No changes.")
        return 0

    headers = {"X-ONETOO-MAINTAINER": token, "User-Agent": "onetoo-autopilot/0.1"}

    # Try likely endpoints for pending list (best-effort)
    list_urls = [
        f"{base}/contrib/v2/pending/list",
        f"{base}/contrib/v2/pending/index",
        f"{base}/contrib/v2/pending/index.json",
    ]

    pending_ids = None
    last_err = None

    for u in list_urls:
        try:
            j = http_get_json(u, headers=headers)
            if isinstance(j, dict) and isinstance(j.get("items"), list):
                pending_ids = [it.get("id") for it in j["items"] if isinstance(it, dict) and it.get("id")]
                break
            if isinstance(j, dict) and isinstance(j.get("ids"), list):
                pending_ids = [x for x in j["ids"] if isinstance(x, str)]
                break
            if isinstance(j, list):
                pending_ids = [x for x in j if isinstance(x, str)]
                break
        except Exception as e:
            last_err = e

    if pending_ids is None:
        print("autopilot: could not discover pending list endpoint (safe exit).")
        if last_err:
            print("autopilot: last error:", repr(last_err))
        return 0

    pending_ids = [x for x in pending_ids if x]
    print(f"autopilot: discovered {len(pending_ids)} pending ids")

    out_doc = {
        "schema": "onetoo-ai-search-accepted-set/v1",
        "version": "1.0",
        "updated_at": now_z(),
        "lane": "sandbox",
        "note": "Autopilot sandbox set (unsigned). Stable accepted-set stays maintainer-signed.",
        "items": []
    }

    seen_urls = set()

    for pid in pending_ids[:200]:  # safety cap
        try:
            pj = http_get_json(f"{base}/contrib/v2/pending/get?id={pid}", headers=headers)
        except Exception as e:
            print("autopilot: failed to fetch pending id:", pid, "err:", repr(e))
            continue

        body = pj.get("body", pj) if isinstance(pj, dict) else pj
        if not isinstance(body, dict):
            continue

        if body.get("kind") != "publisher":
            continue

        url = body.get("url")
        if not isinstance(url, str) or not url.startswith("http"):
            continue

        if url in seen_urls:
            continue
        seen_urls.add(url)

        item = dict(body)
        item["added_from_pending"] = pid
        out_doc["items"].append(item)

    safe_write("dumps/contrib-autopilot.json", out_doc)
    safe_write("public/dumps/contrib-autopilot.json", out_doc)

    print(f"autopilot: wrote {len(out_doc['items'])} items to contrib-autopilot.json (sandbox)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
