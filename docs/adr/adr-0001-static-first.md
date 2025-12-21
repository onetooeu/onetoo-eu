# ADR-0001: Static-first deployment on Cloudflare Pages
Date: 2025-12-19
Status: Accepted

## Context
We need extreme availability, low operational burden, and easy global distribution.

## Decision
Use static hosting (Cloudflare Pages) for docs and public datasets. Keep interfaces versioned and integrity-protected.

## Consequences
- Very low ops overhead
- Fast global access
- Changes require careful versioning and changelog discipline
