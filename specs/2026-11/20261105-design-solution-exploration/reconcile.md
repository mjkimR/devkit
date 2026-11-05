---
reconcile_id: REC-design-solution-exploration
status: pending
targets:
  - file: docs/capabilities/delivery/CAP-DLV-design-exploration.md
    resolution: modified
  - file: docs/usecases/delivery/UC-explore-a-design-problem.md
    resolution: modified
  - file: docs/architecture/ARCH-05-2-components.md
    resolution: modified
  - file: docs/decisions/2026-11/20261105-explicit-solution-exploration.md
    resolution: modified
  - file: packages/devkit-catalog/README.md
    resolution: modified
  - file: guides/install/bundle-recommendations.md
    resolution: modified
---

# Reconciliation: `SPEC-design-solution-exploration`

- `CAP-DLV-design-exploration` reflects opt-in invocation, general solution mechanisms, optional local roles,
  independent first passes/fallback, bounded evidence/criticism and coordinator-owned output authority (AC-01–06).
- `UC-explore-a-design-problem` covers the normal design discussion and extensions for missing facts, simple inline
  work, missing fresh contexts, partial evidence, zero criticism findings and requested or blocked destinations.
- `ARCH-05-2-components` adds only the design_explore content layout; runtime/dependency/feature edges are unchanged.
- `ADR-explicit-solution-exploration` keeps its accepted decision and gains final capability clause traces.
- Catalog README and installation recommendations name the explicit general design entry and opt-in selection.
- Entrypoints use the skill router; bundle directories, role internals, tests, metadata and architecture config are
  not suitable code doorways for either new document.
- No product screens, durable domain terms, runtime APIs or deferred required work are introduced.
- Verification covers packaging and stated instruction consistency, not obedience, creativity or comparative benefit.
