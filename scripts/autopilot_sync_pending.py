#!/usr/bin/env python3
# ONETOO Autopilot (decade-grade): pending -> accepted + audit log + append-only ledger + deterministic snapshot
import os, json, sys, datetime, hashlib, subprocess
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

def now_z():
    # UTC ISO8601 without ms (stable)
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def jcanon(obj) -> str:
    # canonical JSON for stable hashing
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def safe_mkdir(path: str):
    os.makedirs(path, exist_ok=True)

def safe_read_json(path: str, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def safe_write_text(path: str, text: str):
    d = os.path.dirname(path)
    if d:
        safe_mkdir(d)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)

def safe_write_json(path: str, obj):
    safe_write_text(path, json.dumps(obj, ensure_ascii=False, indent=2) + "\n")

def http_get_json(url: str, headers=None, timeout=25):
    # match curl behavior (Accept + no-cache)
    base_headers = {
        "Accept": "application/json",
        "Cache-Control": "no-cache",
        "User-Agent": "onetoo-autopilot/0.1",
    }
    headers = headers or {}
    base_headers.update(headers)
    req = Request(url, headers=base_headers, method="GET")
    with urlopen(req, timeout=timeout) as r:
        data = r.read().decode("utf-8", errors="replace")
    return json.loads(data)

def minisign_sign_if_possible(input_path: str, output_sig_path: str) -> bool:
    # Signs using ~/.minisign/minisign.key if minisign is available.
    # Optional passphrase via MINISIGN_PASS.
    key_path = os.path.expanduser("~/.minisign/minisign.key")
    if not os.path.exists(key_path):
        return False
    try:
        subprocess.run(["minisign", "-v"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    except Exception:
        return False

    env = os.environ.copy()
    # minisign reads passphrase from tty; but supports MINISIGN_PASSWORD in some setups.
    # We'll try both common envs without breaking if ignored.
    if env.get("MINISIGN_PASS"):
        env["MINISIGN_PASSWORD"] = env["MINISIGN_PASS"]

    # -S signs file, -s private key, -x signature output
    try:
        subprocess.run(
            ["minisign", "-S", "-s", key_path, "-m", input_path, "-x", output_sig_path],
            check=True,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return True
    except Exception:
        return False

def month_key(ts_z: str) -> str:
    # "2026-01" from "2026-01-10T18:10:26Z"
    return ts_z[:7]

def append_jsonl(path: str, obj):
    d = os.path.dirname(path)
    if d:
        safe_mkdir(d)
    line = jcanon(obj) + "\n"
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(line)

def ledger_last_hash(ledger_path: str) -> str:
    if not os.path.exists(ledger_path):
        return "0" * 64
    last = None
    with open(ledger_path, "r", encoding="utf-8", errors="replace") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                last = ln
    if not last:
        return "0" * 64
    try:
        obj = json.loads(last)
        h = obj.get("entry_hash")
        if isinstance(h, str) and len(h) == 64:
            return h
    except Exception:
        pass
    return "0" * 64

def decide(body: dict, heuristics: dict):
    """
    Returns (decision, reason, score, lane)
    decision: "accept" | "sandbox" | "reject"
    """
    # Minimal hard checks (safe defaults)
    url = (body.get("url") or "").strip()
    wk  = (body.get("wellKnown") or "").strip()
    kind = (body.get("kind") or "").strip()

    if kind not in ("publisher", "dataset", "tool", "site", "feed", "repo", ""):
        return ("sandbox", "unknown_kind", 0, "sandbox")

    # hard reject rules from heuristics.json (if present)
    rejects = heuristics.get("auto_reject", [])
    for r in rejects:
        try:
            field = r.get("field")
            op = r.get("op")
            val = r.get("value")
            v = body.get(field, "")
            if op == "equals" and v == val:
                return ("reject", f"rule_reject:{field}=={val}", 0, "sandbox")
            if op == "contains" and isinstance(v, str) and isinstance(val, str) and val in v:
                return ("reject", f"rule_reject:{field}~{val}", 0, "sandbox")
        except Exception:
            continue

    # Basic validity -> otherwise sandbox
    if not url.startswith("https://"):
        return ("sandbox", "url_not_https", 0, "sandbox")
    if wk and not wk.startswith("https://"):
        return ("sandbox", "wellKnown_not_https", 0, "sandbox")

    # scoring (very lightweight; can be expanded later)
    score = 0
    if body.get("title"): score += 1
    if body.get("description"): score += 1
    if body.get("repo"): score += 1
    if isinstance(body.get("languages"), list) and len(body["languages"]) > 0: score += 1
    if isinstance(body.get("topics"), list) and len(body["topics"]) > 0: score += 1
    if wk: score += 1

    # auto-sandbox rules from heuristics.json (if present)
    sandbox_rules = heuristics.get("auto_sandbox", [])
    for r in sandbox_rules:
        try:
            field = r.get("field")
            op = r.get("op")
            val = r.get("value")
            v = body.get(field, "")
            if op == "missing" and (v is None or v == "" or v == []):
                return ("sandbox", f"rule_sandbox:{field}_missing", score, "sandbox")
            if op == "contains" and isinstance(v, str) and isinstance(val, str) and val in v:
                return ("sandbox", f"rule_sandbox:{field}~{val}", score, "sandbox")
        except Exception:
            continue

    # stable threshold (default: >=3)
    stable_min = int(heuristics.get("stable_min_score", 3))
    if score >= stable_min:
        return ("accept", "score_ok", score, "stable")
    return ("sandbox", "score_low", score, "sandbox")

def main():
    if os.getenv("ONETOO_AUTOPILOT_ENABLED", "").strip() != "1":
        print('autopilot: disabled (set ONETOO_AUTOPILOT_ENABLED=1 to enable). No changes.')
        return 0

    base = os.getenv("ONETOO_SEARCH_BASE", "https://search.onetoo.eu").strip().rstrip("/")
    token = os.getenv("ONETOO_MAINTAINER_TOKEN", "").strip()
    if not token:
        print("autopilot: missing ONETOO_MAINTAINER_TOKEN. No changes.")
        return 0

    headers = {"X-ONETOO-MAINTAINER": token}

    # discover pending list endpoint (confirmed working: /contrib/v2/pending)
    pending_url = f"{base}/contrib/v2/pending"
    try:
        pend = http_get_json(pending_url, headers=headers)
    except Exception as e:
        print("autopilot: could not discover pending list endpoint (safe exit).")
        print(f"autopilot: last error: {repr(e)}")
        return 0

    items = pend.get("items") or []
    ids = [x.get("id") for x in items if isinstance(x, dict) and x.get("id")]
    print(f"autopilot: discovered {len(ids)} pending ids")

    # load heuristics (optional)
    heuristics = safe_read_json("autopilot/heuristics.json", {})
    if not isinstance(heuristics, dict):
        heuristics = {}

    # load current accepted-set doc as base (keeps schema/version fields if you already have them)
    accepted = safe_read_json("dumps/contrib-accepted.json", {
        "schema": "onetoo-ai-search-accepted-set/v1",
        "version": "1.0",
        "updated_at": now_z(),
        "lane": "stable",
        "note": "Autopilot managed accepted set (stable).",
        "items": []
    })
    if "items" not in accepted or not isinstance(accepted["items"], list):
        accepted["items"] = []

    accepted_map = {}
    for it in accepted["items"]:
        try:
            k = it.get("added_from_pending") or it.get("url") or jcanon(it)
            accepted_map[k] = it
        except Exception:
            pass

    # setup decade-grade dirs
    safe_mkdir("autopilot/logs")
    safe_mkdir("autopilot/ledgers")
    safe_mkdir("autopilot/state")

    ts = now_z()
    mkey = month_key(ts)
    log_path = f"autopilot/logs/{mkey}.jsonl"
    ledger_path = "autopilot/ledgers/ledger.jsonl"
    prev_hash = ledger_last_hash(ledger_path)

    changed = False
    decisions = []

    for pid in ids:
        # fetch pending body
        get_url = f"{base}/contrib/v2/pending/get?id={pid}"
        try:
            resp = http_get_json(get_url, headers=headers)
        except Exception as e:
            decisions.append({"id": pid, "decision": "error", "error": repr(e)})
            continue

        if not resp.get("ok"):
            decisions.append({"id": pid, "decision": "error", "error": resp.get("error", "unknown")})
            continue

        body = resp.get("body") or {}
        if not isinstance(body, dict):
            decisions.append({"id": pid, "decision": "error", "error": "body_not_object"})
            continue

        decision, reason, score, lane = decide(body, heuristics)

        # audit record (JSONL)
        audit = {
            "ts": ts,
            "pending_id": pid,
            "decision": decision,
            "lane": lane,
            "reason": reason,
            "score": score,
            "url": body.get("url"),
            "wellKnown": body.get("wellKnown"),
            "repo": body.get("repo"),
        }
        append_jsonl(log_path, audit)

        # ledger entry (append-only hash-chain)
        payload = {
            "ts": ts,
            "pending_id": pid,
            "decision": decision,
            "lane": lane,
            "reason": reason,
            "score": score,
            "body": body,  # full input for deterministic replay
        }
        payload_json = jcanon(payload).encode("utf-8")
        entry_hash = sha256_hex((prev_hash + "\n").encode("utf-8") + payload_json)
        entry = {
            "prev_hash": prev_hash,
            "entry_hash": entry_hash,
            "payload": payload,
        }
        append_jsonl(ledger_path, entry)
        prev_hash = entry_hash

        decisions.append({"id": pid, "decision": decision, "lane": lane, "reason": reason, "score": score})

        # apply decision to accepted-set (stable only)
        if decision == "accept":
            item = dict(body)
            item["added_from_pending"] = pid
            key = item.get("added_from_pending") or item.get("url")
            if key not in accepted_map:
                accepted["items"].append(item)
                accepted_map[key] = item
                changed = True

    # update accepted metadata
    accepted["updated_at"] = ts
    accepted["lane"] = "stable"

    # deterministic snapshot for replay
    snapshot = {
        "schema": "onetoo-autopilot-run-snapshot/v1",
        "ts": ts,
        "search_base": base,
        "pending_count": len(ids),
        "decisions": decisions,
        "accepted_items_count": len(accepted.get("items", [])),
        "ledger_last_hash": prev_hash,
        "rules": heuristics,
    }
    snap_name = f"autopilot/state/run-{ts.replace(':','').replace('-','')}.json"
    safe_write_json(snap_name, snapshot)

    # write accepted-set if changed OR always (to refresh updated_at)
    safe_write_json("dumps/contrib-accepted.json", accepted)
    safe_write_json("public/dumps/contrib-accepted.json", accepted)

    # sign accepted-set if possible
    signed = minisign_sign_if_possible("dumps/contrib-accepted.json", "dumps/contrib-accepted.json.minisig")
    if signed:
        # mirror signature into public
        try:
            sig = open("dumps/contrib-accepted.json.minisig", "rb").read()
            safe_mkdir("public/dumps")
            with open("public/dumps/contrib-accepted.json.minisig", "wb") as f:
                f.write(sig)
        except Exception:
            pass

    print(f"autopilot: wrote accepted-set items={len(accepted.get('items', []))}")
    print(f"autopilot: audit_log={log_path}")
    print(f"autopilot: ledger_last_hash={prev_hash}")
    print(f"autopilot: snapshot={snap_name}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
