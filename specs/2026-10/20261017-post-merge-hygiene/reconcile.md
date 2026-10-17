---
reconcile_id: REC-post-merge-hygiene
feature: SPEC-post-merge-hygiene
status: resolved
targets:
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/architecture/ARCH-05-1-containers.md
    resolution: modified
  - file: docs/architecture/ARCH-07-deployment.md
    resolution: modified
  - file: docs/development/ci-cd.md
    resolution: modified
  - file: docs/README.md
    resolution: modified
---

# Reconciliation: Post-integration hygiene

`CAP-HARN-agent-guidance` records the seed validity and installed-package verification requirements and aligns its
asset inventory with the bundle manifest. `ARCH-05-1-containers` includes the SDD package; `ARCH-07-deployment`
includes its independently versioned release wheel and correct projection/worktree locations. The CI reference
matches the existing reusable/manual workflow and its working-tree rules check; no trigger was changed. The docs
entry guide retains completed specs as work history in accordance with the constitution.

Package and root quick references, the root agent package list, release installation notes and the distributed
reference-rule guide are aligned with the monorepo. These do not introduce a new capability or user journey.
Previously seeded consumer files remain project-owned; only newly seeded metadata changes.

The existing guidance entrypoints already cover the seed and distributed guide directories. Mechanically derived
README, agent-guide and release-script paths are not guidance implementation entrypoints; the package regression
test is verification rather than an additional runtime entrypoint. No entrypoint additions are required.

No work from the approved scope is deferred.
