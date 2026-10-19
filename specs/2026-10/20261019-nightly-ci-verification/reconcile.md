---
reconcile_id: REC-nightly-ci-verification
status: pending
targets:
  - file: docs/development/ci-cd.md
    resolution: modified
  - file: docs/development/workflow.md
    resolution: modified
  - file: docs/development/setup.md
    resolution: modified
  - file: docs/decisions/2026-10/20261019-nightly-ci-verification.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
---

# Reconciliation: `SPEC-nightly-ci-verification`

The repository CI guide and accepted `ADR-nightly-ci-verification` define successful-head nightly gating,
manual/release full coverage, failure retries and delayed regression discovery. Development and setup docs name
affected-only local verification. `CAP-HARN-agent-guidance` reflects repository policy and result reuse in shipped
planning/review/integration skills. Its existing skills directory entrypoint already covers all three changed
skills; the nightly workflow and repository guide are not capability-owned code entrypoints.

The capability reflection extends Task 2's expected boundary to state the durable consumer-facing skill contract.
No runtime capability, story, architecture or API changed; the workflow stage definitions and checks are unchanged.
