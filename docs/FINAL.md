# ONETOO Trust Hub — Final release

This repository snapshot is intended as a long-lived, stable trust hub for **onetoo.eu**.

- Version: **2025.12-final**
- Frozen date: **2025-12-19**
- Primary trust anchor: **minisign signatures** over `dumps/sha256.json` and release metadata
- Optional attestations: **Sigstore/Cosign bundles** + **SLSA provenance** for release tags

The goal is stability and backward compatibility:
- Core endpoints remain stable (`/.well-known/ai-trust-hub.json`, `/.well-known/security.txt`, `/.well-known/llms.txt`).
- Aliases are provided (`/hub`, `/trust`, `/verify`) without breaking the existing routes.

