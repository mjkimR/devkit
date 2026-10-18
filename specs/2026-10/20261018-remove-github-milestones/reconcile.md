---
reconcile_id: REC-remove-github-milestones
feature: SPEC-remove-github-milestones
status: pending
targets:
  - file: docs/architecture/ARCH-05-1-containers.md
    resolution: modified
---

# Reconciliation: Remove GitHub milestone guidance

The architecture catalog example now names host-observer, matching the only remaining catalog entry point.
Consumer READMEs, installation recommendations and new-repository questions are updated in the same change.
`CAP-DIST-content-packages` keeps its existing packaging contract; no API or schema changes are required.
`ADR-roadmap-in-repository` and the document milestone implementation are preserved. No work is deferred.
