# ONETOO Autopilot Ledgers (append-only)

Purpose:
- decade-grade, append-only history of autopilot decisions
- deterministic replay (given the same inputs, rules and code)
- tamper-evident chain (each entry links to previous hash)

Files:
- ledger.jsonl: newline-delimited JSON entries, append-only
- ledger.sha256: rolling hash of the ledger file (optional helper)
