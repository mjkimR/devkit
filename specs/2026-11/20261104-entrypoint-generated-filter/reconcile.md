---
reconcile_id: REC-entrypoint-generated-filter
status: resolved
targets:
  - file: docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md
    resolution: modified
---

# Reconciliation: `SPEC-entrypoint-generated-filter`

## Reflection

`CAP-TRACE-code-entrypoints` restates managed-output ownership, output-only versus mixed directories, absent and
malformed receipts, explicit-selector refusal and the stable skip reason. The shared scope/path contract and
manual declarations remain unchanged. Existing entrypoints already include the whole entrypoints feature and its
CLI doorway; no new declaration is needed. No structural change or new domain term needs an architecture/glossary
update. No development reference for entrypoints exists in this checkout.

## Source feedback outcome

`FB-entrypoints-derive-offers-managed-paths` is resolved by the complete direct fix. It retains the original
suggestion and records why ownership filtering preserves authored ignored paths. Focused98 and full6550 tests,
independent Code Review and the three-to-zero real-bundle comparison verify the outcome.

## Deferred work

None in the agreed scope.
