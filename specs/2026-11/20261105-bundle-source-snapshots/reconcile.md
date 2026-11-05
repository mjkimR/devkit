---
reconcile_id: REC-bundle-source-snapshots
status: pending
targets:
  - file: docs/capabilities/distribution/CAP-DIST-in-repo-bundles.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-content-packages.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-workspace-ownership.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
    resolution: modified
  - file: docs/usecases/distribution/UC-snapshot-bundle-sources.md
    resolution: modified
  - file: docs/architecture/ARCH-05-2-components.md
    resolution: modified
  - file: docs/development/reference/distribution.md
    resolution: modified
  - file: guides/install/existing-repository.md
    resolution: modified
  - file: docs/steering/glossary.md
    resolution: modified
---

# Bundle source snapshot reconciliation

The local-package capability owns supported sources, complete wrapping, canonical provenance, guarded adoption,
captured-tree drift protection and recovery. Content packages retain global uniqueness and explicit reinstall;
workspace ownership and sync retain config/receipt/override boundaries. The use case covers each refusal,
recovery and fresh-consumer outcome. Architecture adds only distribution command entrypoints.
Quick reference and consumer instructions are kept aligned.

The Host expressly admitted one glossary row for Bundle source snapshot, distinct from governance Snapshot run.
It adds no capability or synonym mapping. The promoted ADR decision is unchanged and needs no source edit.
No implementation work is deferred; runtime vendoring and automatic source access remain excluded.
Entry-point candidate review and independent reconciliation verification follow before resolving this record.

Chosen doorways are distribution CLI bundles.py and typed usecases/snapshots.py for the local-package capability
and new use case. Existing discovery, workspace and sync doorways remain for their owning contracts.
Models, repository helpers, source service directory, instructions and tests were rejected as new doorway
candidates. The full current scope remains one distribution feature; no new package/feature edge or UI screen.
