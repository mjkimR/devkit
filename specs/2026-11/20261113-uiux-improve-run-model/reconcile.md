---
reconcile_id: REC-uiux-improve-run-model
status: pending
targets:
  - file: docs/capabilities/delivery/CAP-DLV-uiux-improvement.md
    resolution: modified
  - file: docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md
    resolution: modified
  - file: docs/decisions/2026-11/20261113-uiux-task-approved-run.md
    resolution: modified
  - file: docs/decisions/2026-11/20261105-uiux-improvement-workflow-boundary.md
    resolution: modified
  - file: docs/decisions/2026-11/20261110-impeccable-session-authority.md
    resolution: modified
---

# Reconcile: SPEC-uiux-improve-run-model

The capability and use case reflect explicit per-task route selection, no-answer waiting, prior-authority reuse,
selected-workflow required reviews, checks on both routes, scope bounds, separate Git authority and report-only
stale-document follow-up. The promoted ADR and the two handoff-written predecessor pointers precisely record
partial supersession; both old decisions remain accepted with their other clauses effective.

The entry, orchestration, guide and contract assertions implement AC-01..AC-09. The installed-consumer E2E verifies
independent distribution and selection-neutral configuration. No runtime, package or feature edge changed.
Entrypoints remain the existing entry skill. Derivation candidates for the broad bundle source root and both
test paths were rejected: the root is not the user entry, and tests are verification rather than doorways.

No required criterion is deferred. Interactive question/load routing remains owned by
`PROP-uiux-improve-impeccable-routing`; pilot instruction hygiene remains owned by
`PROP-uiux-improve-bundle-hygiene`. Live model/host trials, comparative quality and defect parity remain unverified
best-effort evidence, not deferred required functionality.
