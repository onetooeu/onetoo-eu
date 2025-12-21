# CI Signing (minisign)

This repo can automatically:
1) regenerate `dumps/sha256.json`
2) sign `dumps/sha256.json`, `dumps/release.json`, `dumps/release-mega.json`
3) publish the public key at `/.well-known/minisign.pub`

## Required secrets
- `MINISIGN_SECRET_KEY_B64` — base64 of the minisign secret key file

## Optional secrets
- `MINISIGN_PUBLIC_KEY_LINE` — public key line (so CI can publish/update it)
- `MINISIGN_PASSWORD` — if your secret key is password-protected

Workflow: `.github/workflows/trusthub-sign.yml`
