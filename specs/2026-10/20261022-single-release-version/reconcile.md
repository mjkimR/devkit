---
reconcile_id: REC-single-release-version
status: pending
targets:
  - file: docs/architecture/ARCH-07-deployment.md
    resolution: modified
  - file: docs/development/ci-cd.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-single-release-version.md
    resolution: modified
---

# Reconciliation: `SPEC-single-release-version`

`ARCH-07-deployment` describes one workspace-wide version and its release checks.
`ADR-single-release-version` records the root source and generated static metadata trade-off.
The CI reference and root README show synchronization, lock validation and the release command.
The build retains the separate model version. Public library APIs and frontend npm packaging are unchanged.
This repository tooling change adds no application capability or use case; no CAP/UC entrypoint is applicable.
There is no deferred implementation scope.
