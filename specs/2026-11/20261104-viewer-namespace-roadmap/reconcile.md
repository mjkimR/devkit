---
reconcile_id: REC-viewer-namespace-roadmap
status: pending
targets:
  - file: docs/capabilities/viewer/CAP-VIEW-repository-viewer.md
    resolution: modified
  - file: docs/development/reference/viewer.md
    resolution: modified
  - file: packages/devkit-viewer/README.md
    resolution: modified
  - file: docs/decisions/2026-11/20261104-viewer-namespace-roadmap-discovery.md
    resolution: modified
  - file: docs/materials/2026-11/20261104-viewer-namespace-roadmap/implementation-evidence.md
    resolution: modified
  - file: docs/materials/2026-11/20261104-viewer-namespace-roadmap/baseline.md
    resolution: waived
    rationale: Preserved Planning fixture instructions moved by handoff without changing the measured result.
  - file: docs/materials/2026-11/20261104-viewer-namespace-roadmap/baseline.json
    resolution: waived
    rationale: Preserved Planning baseline data moved by handoff; implementation outcomes are recorded separately.
---

# Reconciliation: `SPEC-viewer-namespace-roadmap`

## Reflection

`CAP-VIEW-repository-viewer` specifies the four structural path forms, registration independence, partial errors,
header-only optimized loading and generic type guarantees. Global and namespace readiness/member resolution uses
the complete set before history filtering. The reference and package README give the same reading scope; the ADR
Confirmation names executable regressions and the preserved baseline. No interface, dependency, identity, milestone,
UX layout or general document-model contract changed.

## Source feedback

`FB-viewer-namespace-roadmap-roots` remains promoted. The implementation now covers its discovery, cross-root
readiness and membership scope; source status is terminal and was not changed by this worker. No required work is
deferred. Registration filtering and validity badges remain the explicitly accepted non-goals, not missing criteria.

## Verification

Actual baseline: one global path before, two including the namespace archived path after, no errors.
Backend discovery/worktree33 tests; affected partial14paths165 tests; frontend130 tests; exact selector frontend
install/lint/check/test/pack/build chain; Python lint/Pyright and frontend lint/check; generated viewer-assets
checked1stale0 all passed. Independent Code Review passed with no findings. Node22.22.0 engine warning and the
unexercised supported-version matrix remain disclosed in the evidence and review. The prior seven-target review passed; root-metadata correction inputs await a fresh bounded check.

## Entrypoints

Derivation returned four pairs: the frontend library, Python repository and static paths are already covered by
existing capability entrypoints. The only new candidate is the integration test directory, rejected as verification
rather than an implementation doorway. No entrypoint write is needed; the capability already owns the viewer package.
