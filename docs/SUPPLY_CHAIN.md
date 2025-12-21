# Supply-chain Trust (Minisign + Sigstore)

ONETOO Trust Hub uses a **dual trust model**:

1) **Minisign (primary, offline-root)**
- Deterministic inventory: `dumps/sha256.json`
- Release metadata: `dumps/release.json`, `dumps/release-mega.json`
- Signatures: `dumps/sigs/*.minisig`
- Public key endpoint: `/.well-known/minisign.pub`

2) **Sigstore/Cosign (optional, CI attestation + transparency log)**
- Keyless signatures for **blobs** (JSON artifacts)
- Output bundles in `dumps/attestations/*.bundle`
- Each bundle includes a Rekor transparency-log inclusion proof.

## Why both?
- Minisign is stable and simple (works offline).
- Sigstore adds modern CI provenance and public transparency log evidence.

## What is the source of truth?
- **Content integrity** is anchored by minisign + `dumps/sha256.json`.
- Sigstore is an **additional attestation** that the CI pipeline produced/checked these artifacts.

## Verify minisign
```bash
curl -fsSL https://onetoo.eu/.well-known/minisign.pub -o minisign.pub
minisign -Vm dumps/sha256.json -p minisign.pub -x dumps/sigs/sha256.json.minisig
```

## Verify cosign (keyless) — example
```bash
# install cosign (see https://docs.sigstore.dev/cosign/)
cosign verify-blob \
  --bundle dumps/attestations/sha256.json.bundle \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  --certificate-identity-regexp 'https://github.com/.+/.+/.github/workflows/cosign-attest.yml@refs/heads/main' \
  dumps/sha256.json
```

> If your default branch is not `main`, update the identity regexp accordingly.
