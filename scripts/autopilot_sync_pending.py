#!/usr/bin/env python3
import os, json, datetime, sys, urllib.parse
from urllib.request import Request, urlopen
from urllib.error import HTTPError

def now_z():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def http_get(url, headers=None, timeout=15):
    headers = headers or {}
    base_headers = {
        "Accept": "application/json",
        "Cache-Control": "no-cache",
        "User-Agent": "onetoo-autopilot/0.2",
    }
    base_headers.update(headers)
    req = Request(url, headers=base_headers, method="GET")
    with urlopen(req, timeout=timeout) as r:
        body = r.read()
        ct = r.headers.get("Content-Type","")
    return body, ct

def http_get_json(url, headers=None, timeout=15):
    body, _ct = http_get(url, headers=headers, timeout=timeout)
    return json.loads(body.decode("utf-8", errors="replace"))

def safe_read_json(path, fallback):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return fallback

def safe_write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)

def append_jsonl(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def normalize_base(base):
    base = (base or "").strip()
    if not base:
        base = "https://search.onetoo.eu"
    return base.rstrip("/")

def join_url(base, path):
    return base.rstrip("/") + "/" + path.lstrip("/")

def host_of(url):
    try:
        return (urllib.parse.urlparse(url).hostname or "").lower()
    except Exception:
        return ""

def load_heuristics():
    return safe_read_json("autopilot/heuristics.json", {})

def eval_hard_fail(item, heur):
    url = item.get("url","")
    parsed = urllib.parse.urlparse(url)
    scheme = (parsed.scheme or "").lower()
    host = (parsed.hostname or "").lower()

    for rule in heur.get("hard_fail", []):
        m = rule.get("match", {})
        if "url_host_in" in m and host in [h.lower() for h in m["url_host_in"]]:
            return rule
        if "url_scheme_in" in m and scheme in [s.lower() for s in m["url_scheme_in"]]:
            return rule
        if "url_scheme_not_in" in m and scheme not in [s.lower() for s in m["url_scheme_not_in"]]:
            return rule
    return None

def probe(url, timeout=15):
    try:
        http_get(url, headers={}, timeout=timeout)
        return True, 200
    except HTTPError as e:
        return False, int(getattr(e, "code", 0) or 0)
    except Exception:
        return False, 0

def score_item(item, heur):
    score = 0
    signals = {}

    url = item.get("url","")
    wk = item.get("wellKnown","") or ""
    repo = item.get("repo","") or ""

    signals["wellKnown_present"] = bool(wk)

    if wk:
        ok, code = probe(wk)
        signals["wellKnown_http_200"] = ok and code == 200

        for name, key in [
            ("minisign.pub", "minisign_pub_200"),
            ("sha256.json", "sha256_json_200"),
            ("security.txt", "security_txt_200"),
        ]:
            ok2, code2 = probe(wk.rstrip("/") + "/" + name)
            signals[key] = ok2 and code2 == 200
    else:
        signals["wellKnown_http_200"] = False
        signals["minisign_pub_200"] = False
        signals["sha256_json_200"] = False
        signals["security_txt_200"] = False

    signals["repo_github"] = repo.startswith("https://github.com/")

    for rule in heur.get("soft_rules", []):
        when = rule.get("when")
        if when and signals.get(when):
            score += int(rule.get("score", 0))

    allow = heur.get("allowlist", {})
    if host_of(url) in [h.lower() for h in allow.get("hosts", [])]:
        score += 20
        signals["allow_host_bonus"] = True
    if any(repo.startswith(pfx) for pfx in allow.get("repos", [])):
        score += 10
        signals["allow_repo_bonus"] = True

    return min(score, 100), signals

def decide(score, hard_fail, heur):
    if hard_fail:
        return "reject"
    d = heur.get("defaults", {})
    accept_t = int(d.get("min_score_to_accept", 70))
    sandbox_t = int(d.get("min_score_to_sandbox", 40))
    if score >= accept_t:
        return "accept"
    if score >= sandbox_t:
        return "sandbox"
    return "reject"

def main():
    if os.getenv("ONETOO_AUTOPILOT_ENABLED", "").strip() != "1":
        print('autopilot: disabled (set ONETOO_AUTOPILOT_ENABLED=1 to enable). No changes.')
        return 0

    token = os.getenv("ONETOO_MAINTAINER_TOKEN", "").strip()
    if not token:
        print("autopilot: missing ONETOO_MAINTAINER_TOKEN. No changes.")
        return 0

    base = normalize_base(os.getenv("ONETOO_SEARCH_BASE", "https://search.onetoo.eu"))
    heur = load_heuristics()
    limits = heur.get("rate_limits", {})
    timeout = int(limits.get("http_timeout_seconds", 15))
    max_pending = int(limits.get("max_pending_per_run", 25))

    pending_url = join_url(base, "/contrib/v2/pending")
    headers = {"X-ONETOO-MAINTAINER": token}

    try:
        pend = http_get_json(pending_url, headers=headers, timeout=timeout)
    except Exception as e:
        print("autopilot: could not discover pending list endpoint (safe exit).")
        print(f"autopilot: last error: {repr(e)}")
        return 0

    items = (pend.get("items") or [])[:max_pending]
    pending_ids = [x.get("id") for x in items if x.get("id")]
    print(f"autopilot: discovered {len(pending_ids)} pending ids")

    accepted = safe_read_json("dumps/contrib-accepted.json", {"schema":"onetoo-ai-search-accepted-set/v1","version":"1.0","updated_at":now_z(),"lane":"stable","note":"Autopilot managed accepted set.","items":[]})
    sandbox = safe_read_json("dumps/contrib-sandbox.json", {"schema":"onetoo-ai-search-sandbox-set/v1","version":"1.0","updated_at":now_z(),"lane":"sandbox","note":"Autopilot sandbox lane.","items":[]})
    rejected = safe_read_json("dumps/contrib-rejected.json", {"schema":"onetoo-ai-search-rejected-set/v1","version":"1.0","updated_at":now_z(),"lane":"rejected","note":"Autopilot rejected lane.","items":[]})

    seen = set()
    for doc in (accepted, sandbox, rejected):
        for it in doc.get("items", []):
            pid = it.get("added_from_pending")
            if pid:
                seen.add(pid)

    decisions = []
    for pid in pending_ids:
        if pid in seen:
            continue

        detail_url = join_url(base, f"/contrib/v2/pending/get?id={urllib.parse.quote(pid)}")
        try:
            det = http_get_json(detail_url, headers=headers, timeout=timeout)
        except Exception as e:
            rec = {"id": pid, "decision":"sandbox", "score":0, "error":repr(e), "at":now_z()}
            decisions.append(rec)
            append_jsonl("dumps/autopilot/audit-log.jsonl", {"event":"decision", **rec})
            continue

        body = det.get("body") or {}
        item = dict(body)
        item["added_from_pending"] = pid

        hard = eval_hard_fail(item, heur)
        score, signals = score_item(item, heur)
        decision = decide(score, hard, heur)

        rec = {"id": pid, "decision": decision, "score": score, "signals": signals, "hard_fail": (hard.get("id") if hard else None), "at": now_z()}
        decisions.append(rec)
        append_jsonl("dumps/autopilot/audit-log.jsonl", {"event":"decision", **rec})

        if decision == "accept":
            accepted["items"].append(item)
        elif decision == "sandbox":
            sandbox["items"].append(item)
        else:
            rejected["items"].append(item)

    ts = now_z()
    for doc in (accepted, sandbox, rejected):
        doc["updated_at"] = ts

    safe_write_json("dumps/contrib-accepted.json", accepted)
    safe_write_json("public/dumps/contrib-accepted.json", accepted)
    safe_write_json("dumps/contrib-sandbox.json", sandbox)
    safe_write_json("public/dumps/contrib-sandbox.json", sandbox)
    safe_write_json("dumps/contrib-autopilot.json", sandbox)
    safe_write_json("public/dumps/contrib-autopilot.json", sandbox)
    safe_write_json("dumps/contrib-rejected.json", rejected)
    safe_write_json("public/dumps/contrib-rejected.json", rejected)

    safe_write_json("dumps/autopilot/decisions.json", {"schema":"onetoo-autopilot-decisions/v1","updated_at":ts,"decisions":decisions})
    safe_write_json("public/dumps/autopilot-decisions.json", {"schema":"onetoo-autopilot-decisions/v1","updated_at":ts,"decisions":decisions})

    print("autopilot: decisions=%d accept=%d sandbox=%d reject=%d" % (
        len(decisions),
        sum(1 for d in decisions if d["decision"]=="accept"),
        sum(1 for d in decisions if d["decision"]=="sandbox"),
        sum(1 for d in decisions if d["decision"]=="reject"),
    ))
    
    # force lane identity (do not inherit stale values from existing files)
    accepted["lane"] = "stable"
    accepted["note"] = "Stable accepted-set used by search (autopilot-managed)."
    sandbox["lane"] = "sandbox"
    sandbox["note"] = "Autopilot sandbox set (unsigned)."
    rejected["lane"] = "rejected"
    rejected["note"] = "Autopilot rejected set."
return 0

if __name__ == "__main__":
    sys.exit(main())
