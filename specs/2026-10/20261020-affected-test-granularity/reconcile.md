---
reconcile_id: REC-affected-test-granularity
feature: SPEC-affected-test-granularity
status: pending
targets:
  - file: docs/development/ci-cd.md
    resolution: modified
  - file: docs/development/workflow.md
    resolution: modified
---

# Reconciliation: `SPEC-affected-test-granularity`

The selector is repository-local development tooling. Its current behavior is defined in the CI and development
workflow references, which now describe per-test-file groups, module-level devkit_spec dependencies, broad default
owners, executed initializers, helpers/conftests, full fallback and runtime-discovery limits. CLI output, runner
handoff, fixed data mappings, MCP consumers, structural tests and complete nightly/manual/release checks retain
their contracts. No product capability, story, namespace boundary or architecture invariant changes.

`ADR-select-tests-by-file-with-finer-spec-dependency-nodes` already records the accepted decision and requires no
additional correction. Dated materials hold reproducible measurements rather than current-state policy. The final
measurements include the independent review fixes and show reductions for gate and two independent spec subareas.
Documents remains broad; no unfulfilled count threshold or performance guarantee is deferred.

No explicitly linked open direct-fix feedback sources were carried into this unit. There is no out-of-boundary
source disposition or retained required implementation work. Future performance investigation is captured in `FB-affected-selector-helper-resolution-cost`;
it is optional and not a substitute for an acceptance requirement.
