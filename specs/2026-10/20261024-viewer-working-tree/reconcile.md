---
reconcile_id: REC-viewer-working-tree
status: resolved
targets:
  - file: docs/capabilities/viewer/CAP-VIEW-repository-viewer.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-viewer.md
    resolution: modified
  - file: docs/decisions/2026-10/20261024-viewer-working-tree.md
    resolution: modified
  - file: docs/development/reference/viewer.md
    resolution: modified
  - file: packages/devkit-viewer/README.md
    resolution: modified
---

The viewer capability now defines saved working-tree reads, current-branch display, path and symlink boundaries, and single-checkout roadmap behavior. `ADR-viewer-working-tree` supersedes the Git-ref reading choice, and the previous ADR is marked superseded. The command reference and package README describe the same endpoint and branch behavior.

`CAP-VIEW-repository-viewer` already points to the browse source and frontend app/library directories, which contain the new entrypoints. Entrypoint derivation also proposed the package README, the whole frontend source directory and browse integration tests; these are not implementation doorways, so no entrypoints changed.
