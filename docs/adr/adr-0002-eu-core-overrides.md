# ADR-0002: EU core + national overrides for jurisdiction engine
Date: 2025-12-19
Status: Accepted

## Context
EU has 27 countries but shared consumer protections; differences are best modeled as overrides.

## Decision
Maintain one EU core policy and small country-specific overrides. Compose deterministically.

## Consequences
- Consistent decisions across EU
- Scales cleanly to all countries
- Easier audits and updates
