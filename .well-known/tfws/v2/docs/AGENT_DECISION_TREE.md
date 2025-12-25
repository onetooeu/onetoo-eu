# TFWS v2 Agent Decision Tree

This file defines a deterministic verification flow for agents that consume TFWS signals.

## Core idea
1) Always verify `key-history.json` using the currently published `minisign.pub`.
2) If optional `trust-state.json` exists, verify it too.
3) Map any mismatch into an incident and downgrade trust.

## Operational notes
- Cache verified results for a short window (e.g., 300s) to reduce load.
- If `key-history.json` fails verification: treat as RED until resolved.
- If only optional artifacts fail: treat as RED for that artifact scope.
