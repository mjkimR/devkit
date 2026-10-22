---
reconcile_id: REC-feedback-planning-parser
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md
    resolution: modified
---

# Reconciliation: `SPEC-feedback-planning-parser`

## Contract reflection

- `CAP-DLV-delivery-workflows` reflects assigned-worktree CLI and instructions, dependency-triggered Host refresh,
  unchanged worker Git restrictions and the payload's ignored in-scope probe path with cleanup and retained evidence.
- `CAP-TRACE-code-entrypoints` names the public text parser, disk/committed consumers, defaults and diagnostics.
  Parser behavior and CLI outputs are unchanged. No glossary term or architecture decision changes.
- Existing entrypoint declarations cover their owned source paths; unrelated cross-product candidates are rejected.

## Source feedback

The four directly addressed open sources are resolved on this branch after independent code review and verification:
`FB-plan-branch-cannot-reference-main-ids`, `FB-planning-reverify-worktree-version-skew`,
`FB-planning-probe-lab-location`, and `FB-reconcile-parser-private-reuse`.
Their dispositions record the direct outcomes; no terminal source is updated. No agreed scope is deferred.
