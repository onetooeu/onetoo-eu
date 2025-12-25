# TFWS v2 — Release gates for v2.0.0

## Gate A — Repository hygiene
- [ ] `v2/` directory present and documented
- [ ] No secrets in repo (`minisign.key`, `.env`, etc.)
- [ ] `.gitignore` includes Windows artifacts and local caches

## Gate B — Schema + examples
- [ ] `trust-state.schema.json` valid (draft 2020-12)
- [ ] `incident.schema.json` valid
- [ ] examples validate structurally (JSON parse + required fields)

## Gate C — Agent behavior
- [ ] Decision tree steps cover:
  - pubkey fetch
  - key-history verify
  - trust-state verify
  - rollback detection (epoch/tag)
  - mirror divergence detection
  - incident escalation states
- [ ] Documented failure outcomes (RED/ORANGE/YELLOW)

## Gate D — Simulation & playbooks
- [ ] Attack simulations list at least:
  - key mismatch
  - rollback
  - cache poison
  - mirror divergence
  - incomplete bundle
- [ ] Operator playbooks exist for each

## Gate E — Integrity checks
- [ ] `python` JSON parse check passes for all v2 JSON artifacts
- [ ] Optional: sha256 inventory generation for v2 folder
- [ ] Optional: signed release notes (minisign) for the v2.0.0 tag

## Gate F — Tagging protocol
- [ ] Tag name: `v2.0.0`
- [ ] Annotated tag message includes:
  - commit id
  - change highlights
  - verification commands
- [ ] Optional: attach generated `v2/` bundle zip with sha256 and minisig
