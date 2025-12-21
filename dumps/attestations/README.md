# Sigstore / Cosign bundles

This folder contains **keyless cosign signature bundles** for core artifacts.

- Bundles: `*.bundle`
- Index: `index.json`

Each bundle contains a Rekor transparency-log inclusion proof.

Verification example:
```bash
cosign verify-blob \
  --bundle dumps/attestations/sha256.json.bundle \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  --certificate-identity-regexp 'https://github.com/.+/.+/.github/workflows/cosign-attest.yml@refs/heads/main' \
  dumps/sha256.json
```
