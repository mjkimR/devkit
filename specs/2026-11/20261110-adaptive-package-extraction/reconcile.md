---
reconcile_id: REC-adaptive-package-extraction
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-adaptive-development.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/usecases/delivery/UC-advance-an-idea.md
    resolution: modified
  - file: docs/usecases/delivery/UC-import-third-party-agent-assets.md
    resolution: modified
  - file: docs/architecture/ARCH-05-1-containers.md
    resolution: modified
  - file: docs/architecture/ARCH-05-2-components.md
    resolution: modified
  - file: docs/architecture/ARCH-07-deployment.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-adaptive-development-and-research.md
    resolution: modified
  - file: docs/decisions/2026-11/20261106-skill-local-swarm-roles.md
    resolution: modified
  - file: docs/decisions/2026-11/20261110-adaptive-dev-distribution.md
    resolution: modified
---

# Reconciliation: `SPEC-adaptive-package-extraction`

| Contract | Reflection and implementation |
| --- | --- |
| `CAP-DLV-adaptive-development` | Independent wheel, install instructions, moved evidence paths and entrypoints; bundle tree unchanged. |
| `CAP-HARN-agent-guidance` | Adaptive entry path and installation owner; deep research remains catalog-owned. |
| `UC-advance-an-idea`, `UC-import-third-party-agent-assets` | Entrypoints move; flows unchanged. |
| `ARCH-05-1-containers`, `ARCH-05-2-components` | Dedicated content package, three initializers, no runtime dependency or feature edge. |
| `ARCH-07-deployment` | Adaptive entry point and installed test move; existing bundle version contract implemented by cross-package baseline lookup. |
| `ADR-adaptive-dev-distribution` | Promoted decision establishes wheel ownership only; no runtime/CLI addition. |
| `ADR-adaptive-development-and-research` | Partial supersession pointer names owning-wheel clauses; Confirmation references follow moved tests; original Outcome retained. |
| `ADR-skill-local-swarm-roles` | Ownership wording repair only. |

The five installation guides describe fresh installs of docs plus adaptive; they add no migration path. Root package inventories and package READMEs name the dedicated owner. No new domain concept or screen is introduced.

Deferred runtime commands and the requirement on devkit-docs remain in `PROP-adaptive-assignment-cli`; lifecycle-hook investigation remains in ~~`PROP-adaptive-lifecycle-hooks`~~ (rejected in `8a725e5d`). Both destinations already exist and no acceptance criterion of this unit is deferred.

Entrypoints were moved one-for-one from their existing bundle asset paths. Broad package and repository-tooling derivation candidates are rejected because they are not these documents' reading doorways.

Independent medium reconcile review covered all ten targets. Its README namespace omission was fixed and rechecked by the implementer; the namespace inventory now includes `devkit_adaptive`.
