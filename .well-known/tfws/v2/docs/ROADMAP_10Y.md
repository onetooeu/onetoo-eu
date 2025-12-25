# TFWS v2 — 10-year roadmap (2026–2035)

This roadmap is intentionally conservative: stable primitives first, then ecosystems.

## Guiding principles
- Deterministic verification over heuristics
- Monotonicity (epoch/tags never go backwards)
- Signed artifacts everywhere (machine + human)
- Compatibility layers for v1.x and ecosystem bridges
- Explicit incident handling as a first-class protocol

---

## Year 0–1 (v2.0 → v2.1): Foundations
### Deliverables
- `trust-state.json` + `trust-state.json.minisig` (canonical v2)
- `incident.json` format + minimal incident feed (append-only)
- Agent decision tree v2 (deterministic)
- Validation tooling:
  - schema validation
  - signature verification
  - inventory verification
- Baseline operator playbooks (key mismatch, rollback, cache poison)

### Hard rules
- `epoch_utc` monotonic (per domain)
- `tag` monotonic (lexicographic or numeric strategy documented)
- Reproducible dumps (same input => same hashes)

---

## Year 1–2 (v2.1 → v2.2): Trust registry + delegation
### Deliverables
- Delegation model:
  - maintainer roles
  - scoped keys (by artifact class)
- Provider registry:
  - who can sign what
  - allowed key rotations
- Cross-origin trust linking (domain A can vouch for domain B) with explicit scopes

---

## Year 2–3 (v2.2 → v2.3): Multi-channel distribution
### Deliverables
- Mirror support (GitHub, Pages, Prod) with divergence detection
- Signed `mirror-state.json` describing authoritative channels
- Optional transparency log hooks (export format; no central dependency required)

---

## Year 3–4 (v2.3 → v2.4): Policy bundles + compliance proofs
### Deliverables
- Signed policy bundles (human + machine readable)
- Standard evidence slots:
  - DPIA references
  - model cards references
  - audit snapshots
- “Compliance delta” artifacts (what changed since last release)

---

## Year 4–5 (v2.4 → v2.5): Agent messaging + safe automation
### Deliverables
- Signed message envelopes
- Inbox/outbox semantics (rate limits, retention)
- Abuse controls and replay protections

---

## Year 5–6 (v2.5 → v2.6): Incident federation
### Deliverables
- Federation of incident feeds across domains
- Standardized severities + remediation confirmations
- Cryptographic proofs of “acknowledged by operator”

---

## Year 6–7 (v2.6 → v2.7): Stronger cryptographic agility
### Deliverables
- Key agility strategy (minisign today, additional methods tomorrow)
- Dual-sign option for rotations (grace window)
- Formal downgrade/rollback prevention profile

---

## Year 7–8 (v2.7 → v2.8): Developer ecosystem
### Deliverables
- SDKs for verification (Go/Python/JS)
- Reference agent implementation
- Conformance test suite

---

## Year 8–9 (v2.8 → v2.9): Governance automation
### Deliverables
- Deterministic policy decision support artifacts
- Signed “decision explanations” (traceable)
- Operator override protocol (signed & logged)

---

## Year 9–10 (v2.9 → v3.0 planning): Next universe
### Deliverables
- v3 design notes (what v2 could not solve)
- Migration guide (v2 → v3)
- Archival strategy for v2 (frozen final)
