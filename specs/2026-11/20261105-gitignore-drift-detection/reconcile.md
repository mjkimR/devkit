---
reconcile_id: REC-gitignore-drift-detection
status: resolved
targets:
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-workspace-ownership.md
    resolution: modified
  - file: docs/development/reference/distribution.md
    resolution: modified
---

# Reconcile: SPEC-gitignore-drift-detection

The sync contract documents the three warning codes, mode precedence, ten-target bounds, failure handling and
read-only behavior implemented by projection_git_notices and covered by test_projection_git.py. Ownership
keeps root ignore/index control with the project and describes desired/previous file sets. The reference lists
all three codes. No new public command, schema or feature edge was introduced.

Self-verification at medium: all changed behavior is within distribution in one package and capability area;
the exact contracts and diff are identified above. The reviewed fixes have real-Git tests including execution of
untracking advice from a different repository. No additional interpretation or cross-component contract remains.
The proposed new use case is unnecessary: diagnostics extend the existing sync operation and are fully covered
by its two capabilities. No delivery behavior is deferred. Framework expansion remains in
PROP-multi-runtime-project-harness and is outside this spec.

Entrypoints: retain sync.py for both capabilities; reject model, repository-directory and test candidates because
they are implementation details rather than operation entry points.
