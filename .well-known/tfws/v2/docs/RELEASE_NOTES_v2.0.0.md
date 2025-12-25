# TFWS v2.0.0 — Release notes (2025-12-25)

## Added
- v2 workspace under `/v2`
- JSON Schemas:
  - `v2/schemas/trust-state.schema.json`
  - `v2/schemas/incident.schema.json`
- Examples:
  - `v2/examples/trust-state.example.json`
  - `v2/examples/incident.example.json`
- Deterministic Agent Decision Tree:
  - `v2/decision-tree.v2.json`
  - `v2/docs/AGENT_DECISION_TREE.md`
- Attack simulations + incident playbooks:
  - `v2/simulations.v2.json`
  - `v2/docs/INCIDENT_PLAYBOOKS.md`
- Roadmap + release gates:
  - `v2/docs/ROADMAP_10Y.md`
  - `v2/docs/RELEASE_GATES.md`
- Integrity inventory:
  - `v2/inventory.sha256`

## Notes
- Inventory is deterministic and can be verified with:
  - `(cd v2 && sha256sum -c inventory.sha256)`
- Incidents are treated as protocol objects (append-only) and are first-class in v2.

