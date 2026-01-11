# ONETOO Add-on (Gold Mid Path): CI autogen deploy marker + sha256 inventory

This add-on is meant to be **dropped into** your existing ONETOO repo.

## What it does
On every push to `main` (and on manual dispatch), CI will:
- ensure root `.well-known/*` is mirrored into `public/.well-known/*`
- regenerate `public/_deploy.txt`
- regenerate `public/.well-known/sha256.json`
- mirror the same JSON into `dumps/sha256.json` and `.well-known/sha256.json`
- commit & push **only if** something changed

## Why
Cloudflare Pages is configured to publish `public/`, so the served marker must live in `public/_deploy.txt`.

## Safety
- It skips execution if the workflow was triggered by `github-actions[bot]` (prevents infinite loops).

## Install
Copy:
- `.github/workflows/ci-autogen-deploy-and-sha256.yml`
- `scripts/ci/gen_artifacts.py`

Then commit & push.

## Notes
- This does **not** sign `.minisig` files (no private keys in CI).
