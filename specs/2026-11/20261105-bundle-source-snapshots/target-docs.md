---
id: PROP-bundle-source-snapshots-target
title: Target contracts for bundle source snapshots
summary: "Exact distribution capability, use case, architecture and consumer guidance changes for local bundle snapshot creation and explicit refresh."
status: draft
proposal: SPEC-bundle-source-snapshots
created_at: 2026-11-05
targets:
  - file: docs/capabilities/distribution/CAP-DIST-in-repo-bundles.md
  - file: docs/capabilities/distribution/CAP-DIST-content-packages.md
  - file: docs/capabilities/distribution/CAP-DIST-workspace-ownership.md
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
  - file: docs/usecases/distribution/UC-snapshot-bundle-sources.md
  - file: docs/architecture/ARCH-05-2-components.md
  - file: docs/development/reference/distribution.md
  - file: guides/install/existing-repository.md
---

# [Blueprint] PROP-bundle-source-snapshots: Target contracts

## Capability and use case targets

Extend `CAP-DIST-in-repo-bundles` with a snapshot section: the ordinary package wrapper, supported static content
package source and rule/helper dependency subset, whole-provider replacement, provenance schema, explicit
create/preview/apply, local edit refusal and unchanged-input idempotence. Specify nonrecursive provenance hashes
and derived bytecode exclusions shared by inventories and drift checks. Validate declarative runtime references
including hooks alongside Python imports, without executing either. State that devkit/runtime/build dependencies
remain separately installed. Add the command entrypoints and test references.

In `CAP-DIST-content-packages`, state that a local wrapper uses unchanged discovery and bundle identities; no
selected-provider precedence is added. Describe multi-bundle replacement and refusal of mixed runtime providers.
Preserve global duplicate-provider errors. Require explicit editable-package reinstall after changed entry-point
metadata and explicit deselection of removed selected bundles. Link the snapshot use case without changing release-version policy.

In `CAP-DIST-workspace-ownership`, distinguish snapshot-owned package sources from project overrides: refresh
refuses source edits; adaptations use existing overrides; subsequent sync retains their upstream drift behavior.
In `CAP-DIST-sync-and-transactions`, state that snapshot creation/refresh does not change selection, receipt or
managed projections; installation and ordinary sync remain explicit subsequent steps.

Create UC-snapshot-bundle-sources at `docs/usecases/distribution/UC-snapshot-bundle-sources.md` with creation,
provider replacement, local dev dependency install, normal sync and explicit preview/apply refresh. Extensions cover
unsupported package/runtime imports, local changes, source drift, duplicate providers, unavailable runtime/build
dependencies and rollback. Link it both ways with the capability. No product screens or UX documents change.

## Architecture and decision targets

Update `ARCH-05-2-components`' distribution summary with source snapshot use cases. Keep CLI/usecase/service/
repository layering, normal source layout and dependency graph. No new cross-feature edge or loader is allowed.
The handoff promotes `ADR-bundle-source-snapshots`; its clauses are restated by the capabilities above.

## Exact implementation and verification paths

| Path or existing parent for a new file | Intended responsibility |
| --- | --- |
| `packages/devkit-dist/src/devkit_dist/features/distribution/cli/bundles.py` | Snapshot/refresh adapters and bounded JSON result wiring. |
| `packages/devkit-dist/src/devkit_dist/features/distribution/usecases/` | Typed source snapshot and explicit refresh operations. |
| `packages/devkit-dist/src/devkit_dist/features/distribution/services/` | Static package support, manifest source closure, provenance, hashes, diff and packaging policy. |
| `packages/devkit-dist/src/devkit_dist/features/distribution/repositories/` | Source inspection and staged local package writes/rollback. |
| `packages/devkit-dist/src/devkit_dist/features/distribution/models/` | Request/result values and stable errors/actions. |
| `packages/devkit-dist/tests/unit/features/distribution/` | Deterministic hash/diff/import-support policy where isolation is useful. |
| `packages/devkit-dist/tests/integration/features/distribution/` | Real source packages, files/modes, path safety, local drift, idempotence after editable discovery, nonrecursive hashes, external declarative handler refusal and injected failure rollback. |
| `packages/devkit-dist/tests/e2e/cli/` | Built local-package consumer, no private-origin dependency, multi-bundle add/remove metadata reinstallation and harness-equipped rule fixture. |
| `packages/devkit-dist/src/devkit_dist/bundles/devkit/bundle/instructions/in-repo-bundle.md` | Source snapshot commands, supported boundaries and exact provider replacement steps. |
| `docs/development/reference/distribution.md` | CLI/schema quick reference matching capability. |
| `guides/install/existing-repository.md` | Private content-package snapshot bootstrap and explicit refresh. |

Generated sync outputs are admitted only when required by changing the selected devkit bundle, according to the
normal worker contract; source asset edits require authoring context. No original content package, release script,
release policy, optional SDD package or foundation source change is planned. Shared distribution documentation and
consumer guidance require serialized handoff/integration with the selective-release unit. Run focused tests,
`just test-dist`, appropriate lint/types/rules and the repository affected-test selector in Development.
