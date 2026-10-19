---
reconcile_id: REC-autonomy-between-approval-gates
feature: SPEC-autonomy-between-approval-gates
status: resolved
targets:
  - file: docs/decisions/2026-10/20261020-autonomy-between-approval-gates.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
---

# Reconciliation: `SPEC-autonomy-between-approval-gates`

`ADR-autonomy-between-approval-gates` records the accepted execution and tool-design principle. The workflow
capability and source spec constitution agree on autonomous routine execution, no incidental human gates,
Host-first worker escalation and preserved mandatory checks, review stops and authority limits.

The constitution is synchronized with `devkit sync`; the generated receipt change records its updated hash.
No runtime behavior, schema, workflow gate or domain terminology changed. No source feedback or deferred
implementation work is part of this documentation task. Existing capability entrypoints are retained because
this change adds policy text, not a new runtime entrypoint.
