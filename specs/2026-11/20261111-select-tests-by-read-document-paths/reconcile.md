---
reconcile_id: REC-select-tests-by-read-document-paths
status: resolved
targets:
  - file: docs/development/ci-cd.md
    resolution: modified
  - file: docs/architecture/ARCH-07-deployment.md
    resolution: modified
---

# Reconcile: `SPEC-select-tests-by-read-document-paths`

## Living Spec impact

- `docs/development/ci-cd.md`: the `just test-affected` bullets describe read discovery (forms, attribution,
  matching, precedence), the frontend bullet says a frontend path selects only its literal readers and keeps the
  frontend check, the untested-paths bullet says those paths select only their literal readers, the result line
  names `reason=reads`, and Limits names readers through imported bases as explicit mappings.
- `ARCH-07-deployment` §1.3 restates the outcome clauses `ADR-literal-read-test-selection` traces to it.
- No capability or use case documents the selector (`devkit docs search "affected test selection"`), so none
  changes; no glossary term is introduced.

## Entrypoints

No capability or use case is a target, so `spec-entrypoints` has no candidate document.

## Source feedback

- `FB-docs-selection-misses-guidance-contract-tests` and `FB-affected-selection-misses-cross-package-fix-scan` are
  `resolved` (terminal): no disposition. Their Disposition lines only had the handoff's rewritten reference worded
  as a delivery by `SPEC-select-tests-by-read-document-paths` instead of a queued proposal.

## Deferred work

- `FB-agents-guide-frontend-selection-wording`: the repository `AGENTS.md` quick reference still says a viewer
  frontend change selects no pytest test; outside this Unit's write scope.
- Retiring `DATA` rows the scan covers stays a later, measured reduction (Non-Goal 1,
  `ADR-literal-read-test-selection` Follow-ups); no destination is opened because no row is planned for removal.
