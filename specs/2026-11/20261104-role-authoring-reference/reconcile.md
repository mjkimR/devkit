---
reconcile_id: REC-role-authoring-reference
status: resolved
targets:
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/decisions/2026-11/20261104-role-authoring-reference.md
    resolution: modified
  - file: docs/decisions/2026-11/20261104-shared-role-authoring.md
    resolution: modified
---

# Reconciliation

`CAP-HARN-agent-guidance` section 4.3 locates detailed role guidance in the skill-authoring reference and preserves
its existing placement and host-limitation semantics. `ADR-role-authoring-reference` partially supersedes only
the location and routing clauses of `ADR-shared-role-authoring`; the earlier decision remains accepted for its
other clauses. No runtime or role behavior changes. Existing harness entrypoints remain appropriate; the
reference is supporting guidance, not a new runtime entrypoint.
