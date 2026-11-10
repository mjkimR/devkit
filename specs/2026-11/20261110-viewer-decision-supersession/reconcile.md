---
reconcile_id: REC-viewer-decision-supersession
status: resolved
targets:
  - file: docs/decisions/2026-11/20261110-viewer-indexed-decision-supersession.md
    resolution: modified
  - file: docs/steering/ux-objects.md
    resolution: modified
  - file: docs/usecases/viewer/UC-read-decision-supersession.md
    resolution: modified
  - file: docs/ux/viewer/UX-view-decision.md
    resolution: modified
  - file: docs/ux/viewer/UX-decision-supersession.md
    resolution: modified
  - file: docs/capabilities/viewer/CAP-VIEW-repository-viewer.md
    resolution: modified
---

# Reconciliation: `SPEC-viewer-decision-supersession`

The viewer capability states the implemented source, parser, freshness, loading, navigation and safe-rendering contracts.
The decision-reading use case, two retained UX documents and shared object register reflect the approved Screens.
The promoted ADR traces its outcome to capability section 4.4. No architecture, glossary or package-edge change is needed.
No required work was deferred and no source feedback was assigned. Actual browser layout remains unverified because
the available CUA browser host was unavailable; DOM interaction tests, frontend checks and generated build are verified.

Entrypoints retain the existing capability package doorways. The use case chooses SddViewer, KnowledgeViews and
SupersessionSummary; generated static files, test files and parser helpers are rejected as navigation entrypoints.
