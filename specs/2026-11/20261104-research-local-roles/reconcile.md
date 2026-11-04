---
reconcile_id: REC-research-local-roles
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-deep-research.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/decisions/2026-11/20261104-skill-local-research-roles.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-adaptive-development-and-research.md
    resolution: modified
---

# Reconciliation

`CAP-DLV-deep-research` states skill-local distribution, general-child invocation, bounded input and factual host
limits. `CAP-HARN-agent-guidance` reflects the same registration boundary. `ADR-skill-local-research-roles`
partially supersedes only the registered-role clauses of `ADR-adaptive-development-and-research`.
`UC-research-an-idea-and-shape-a-roadmap` retains the same research goal and optional roles, so its steps need no edit.
Existing capability entrypoints still name the skill entry; internal role files are not independent entrypoints.
