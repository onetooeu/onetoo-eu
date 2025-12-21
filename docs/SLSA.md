# SLSA provenance for release tags

This repository can generate **SLSA 3+ provenance** for GitHub Release artifacts.

- Workflow: `.github/workflows/slsa-provenance-release-tags.yml`
- Triggers: tags matching `v*` and `release-*`
- Output: GitHub Release asset `provenance.intoto.jsonl`

Minisign remains the **primary trust anchor** for the hosted Trust Hub. SLSA provenance is an additional, verifiable supply-chain signal.
