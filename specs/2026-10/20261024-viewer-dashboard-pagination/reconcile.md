---
reconcile_id: REC-viewer-dashboard-pagination
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
# Reconcile dashboard pagination

`CAP-VIEW-repository-viewer` covers the frontmatter listing transport, first-page body bounds, existing sort priorities with path tie-breakers, page retry, optional host fallback and fixed-expiry snapshot caches. Reference and README mirrors describe these interfaces. Browser YAML parsing, saved working-tree reads, path guards and source identity ownership remain unchanged.

No new architectural dependency, domain term, separate capability or deferred implementation requirement exists. Existing viewer package/library entrypoints cover the new loader and reader. Task 2 includes App.test.ts because selected-repository reads now start at dashboard-list rather than tree.

Entrypoint derivation proposed only packages/devkit-viewer/tests as a new candidate; it was rejected because tests are verification rather than a capability doorway. All implementation paths are already covered by the existing package and library entrypoints.
