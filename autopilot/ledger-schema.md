# Ledger entry schema (v1)

Each line in `autopilot/ledgers/ledger.jsonl` is a JSON object:

Required:
- schema: "onetoo-autopilot-ledger-entry/v1"
- ts: ISO8601 UTC timestamp (Z)
- run_id: unique id for this run (uuid-ish)
- code_ref: git sha of repo at runtime (from GHA / local)
- rules_ref: hash/sha of autopilot rules file(s)
- input:
  - pending_count
  - pending_ids (or hash if too large)
  - search_base
- decision:
  - lane: sandbox|stable|trusted|archived
  - accepted_ids
  - rejected_ids
  - sandboxed_ids
  - reason_codes (array)
- outputs:
  - accepted_set_path(s)
  - minisign_signature_paths
- chain:
  - prev_hash: hex (sha256 of previous ledger line, or "GENESIS")
  - this_hash: hex (sha256 of canonicalized current entry WITHOUT this_hash, then stored)

Notes:
- canonicalization = stable JSON with sorted keys, no whitespace
- append-only: never rewrite historical lines
