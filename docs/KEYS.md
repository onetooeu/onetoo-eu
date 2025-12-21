# Keys & Signatures
ONETOO.eu (operated by **ONETOO.dynamics**) uses cryptographic integrity controls for public datasets.

## Recommended setup (production)
- Maintain a long-lived root key (offline) and a short-lived signing key (online).
- Rotate the online signing key on a regular cadence (e.g., quarterly) or after any suspected compromise.
- Publish public keys under `/.well-known/` and reference them from `api/v1/meta/version.json`.

## Verification
- Verify dataset hashes from `dumps/sha256.json`.
- Verify signatures where applicable (placeholder until your real signing key is installed).

## Key rotation (high level)
1. Generate new signing key (online)
2. Publish new public key
3. Dual-sign for a transition window
4. Deprecate old key and document in changelog
