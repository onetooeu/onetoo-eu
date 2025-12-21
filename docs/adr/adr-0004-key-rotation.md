# ADR-0004: Key rotation and integrity controls
Date: 2025-12-19
Status: Accepted

## Context
Long-lived infrastructure must remain verifiable and resilient to compromise.

## Decision
Adopt an offline root key + rotating online signing key model. Publish verification guidance and changelog all rotations.

## Consequences
- Stronger integrity posture
- Predictable operational playbooks
- Better enterprise audit outcomes
