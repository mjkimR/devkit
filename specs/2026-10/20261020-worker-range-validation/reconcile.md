---
reconcile_id: REC-worker-range-validation
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
---

# Reconciliation: `SPEC-worker-range-validation`

`CAP-DLV-delivery-workflows` defines the inspection interface, committed derivation, source provenance,
pass/fail/not-run semantics, advisory routing, dirty-workflow limitation and Host authority. The accepted
`ADR-informational-range-inspection-reuses-existing-checks` remains unchanged. No architecture, approval,
worker-envelope schema or other capability contract changes are required: inspection composes existing checks.

The package README and spec-delegate/spec-orchestrate guidance point Hosts to the command and require actual
compared heads and changed paths in reviewer payloads. Entrypoints select the worker implementation and the two
affected skills; broad CLI/tests candidates do not represent ownership of the whole package and are omitted.

## Source feedback disposition

- `FB-reconcile-reviewer-no-diff-list` is resolved: reviewer payload guidance now requires the actual changed-path
  list and compared commits. Git fixture tests verify derivation of that information, independent code review
  verified the behavior, and the independent reconciliation payload carries this branch's complete path list.
- `FB-worker-scope-misses-link-repairs` remains outside this command's scope: automatic ownership or scope expansion
  is excluded and its existing feedback retains that follow-up.
- `FB-handoff-premise-drift-unreported` remains outside this command's scope: this run checked its handoff premises,
  but implements no general drift-reporting policy. Its existing feedback retains that follow-up.

No required acceptance criterion is deferred. The latter two feedback files are outside this worker's write
boundary and require no status change; their dispositions are reported for the Host.
