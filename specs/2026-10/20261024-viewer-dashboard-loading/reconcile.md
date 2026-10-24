---
reconcile_id: REC-viewer-dashboard-loading
status: resolved
targets:
  - file: docs/capabilities/viewer/CAP-VIEW-repository-viewer.md
    resolution: modified
  - file: docs/development/reference/viewer.md
    resolution: modified
  - file: packages/devkit-viewer/README.md
    resolution: modified
  - file: packages/devkit-viewer/frontend/README.md
    resolution: modified
---

# Dashboard loading reconciliation

`CAP-VIEW-repository-viewer` owns selective reads, independent section states, 30-second caches, source isolation, refresh and the recursive metadata API. Both READMEs and the HTTP quick reference reflect these contracts.
No architectural decision changes: browser parsing, source injection and read-only saved-file access remain intact.
Existing capability entrypoints cover the backend and frontend directories; helpers and tests add no doorway.

Self-verification is appropriate at medium: one package and one capability area changed, every behavioral contract is identified above, and the regression checks directly cover AC-01 through AC-06.

The broader performance review retains cold knowledge-tab anchor loading as `FB-viewer-knowledge-anchor-loading` and eager book rendering as `FB-viewer-book-rendering`. These are concrete follow-ups, not unfinished dashboard criteria.
