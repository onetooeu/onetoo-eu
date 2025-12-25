# TFWS v2.0.4 — Release Notes

Date: 2025-12-25

## Added
- Policy pack under `policy/`:
  - `agent-decision-contract.json`
  - `trust-levels.json`
  - `trust-state.template.json`
- Release pointers under `releases/`:
  - `releases/v2.0.4.json` + `.minisig`
  - `releases/latest.json` + `.minisig`
- Signed changelog:
  - `changelog.json` + `.minisig`
  - `changelog.feed.xml` + `.minisig`

## Fixed
- Restored `index.json` and ensured it lists policy pack and changelog/feed pointers.
- Canonical redirects for TFWS v2 root and changelog/feed aliases.

## Notes
- Inventory (`inventory.sha256`) remains the canonical list of artifacts for verification.
