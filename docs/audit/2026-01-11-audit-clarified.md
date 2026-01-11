# ONETOO – Audit note (clarified)
**Snapshot:** 11 Jan 2026 (evening, Europe/Bratislava)  
**Scope:** *core trust-root integrity + basic endpoint availability*  
**Status:** ✅ core trust-root healthy; ⚠️ minor secondary endpoint issue (search.onetoo.eu returns 404)

---

## The sentence we are keeping (with precise meaning)

> **“No serious errors: everything holds; minor issues (e.g., search.onetoo.eu 404) are not critical for the core trust-root.”**

This is **true** as long as **none** of the following “serious error” conditions occur:

- deploy marker differs between canonical domains (apex / www / pages.dev)
- `/.well-known/sha256.json` exists but does **not** match the published file tree (tampering)
- CI produces inconsistent artifacts for the same commit (non-determinism)
- system requires manual intervention from the author to remain valid
- trust-root cannot be audited without “social trust”

**Observed:** none of the above are happening in the verified snapshot.

---

## What “minor issues” currently means (and why)

| Problem / Situation | Verified status (11 Jan 2026) | Critical for core trust-root? | Why it is not a serious error | Impact |
|---|---:|---:|---|---|
| `search.onetoo.eu` returns 404 | **Yes** (still 404) | **Low** | Search is an application layer; core trust-root is `.well-known` + inventory + markers | Affects AI-search feature only (secondary) |
| `/.well-known/sha256.json` on domains | Exists + valid JSON | **None** | Canonical inventory is present and consistent with repo & Pages output | Core auditability restored |
| `dumps/sha256.json` (legacy mirror) | Exists + consistent | Low | Mirror only; canonical is `/.well-known/sha256.json` | Optional parity for tooling |
| “No new commits after 11 Jan” | Quiet / stable | None | “Publish & Forget” is intended: reduce churn | Supports decade-stable anchor |
| Homepage + `.well-known/*` | OK / consistent | None | Trust signals are live; deploy marker points to expected commit | Fully functional |

### Summary
The only non-ideal point is **search.onetoo.eu 404**.  
It does **not** affect the core trust-root properties: **integrity, auditability, determinism, autonomy**.

---

## Why search.onetoo.eu 404 is not core-critical (simple model)

**Core trust-root =**
- `/.well-known/deploy.txt`
- `/.well-known/sha256.json`
- signed `.well-known/*` trust files + ledgers

**Search API =** application layer (useful, but not required to keep trust-root truthful).

Analogy:
- Trust-root = the bridge.
- Search API = a coffee stand on the bridge.
If the stand is closed, the bridge still holds.

---

## Re-audit checklist (quick)

1. Deploy marker is readable on both domains.
2. Deploy marker `commit:` equals the currently expected Git commit.
3. `sha256.json` is readable on both domains.
4. `sha256.json` `commit` and `updated_at` are consistent with the last autogen run.
5. Optional: verify `minisign.pub` + signatures if present in `.well-known`.

Use the scripts in `scripts/local/` to automate (read-only checks).

---
