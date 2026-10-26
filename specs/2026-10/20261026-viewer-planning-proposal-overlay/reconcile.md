---
reconcile_id: REC-viewer-planning-proposal-overlay
status: pending
targets:
  - file: docs/capabilities/viewer/CAP-VIEW-repository-viewer.md
    resolution: modified
  - file: docs/decisions/2026-10/20261026-viewer-planning-proposal-overlay.md
    resolution: modified
  - file: docs/decisions/2026-10/20261024-viewer-working-tree.md
    resolution: modified
  - file: docs/development/reference/viewer.md
    resolution: modified
  - file: packages/devkit-viewer/README.md
    resolution: modified
  - file: packages/devkit-viewer/frontend/README.md
    resolution: modified
---
# Reconcile the Planning proposal overlay

`CAP-VIEW-repository-viewer` now holds the delivered contract: the `planning-proposals` endpoint and the `source`
parameter of `tree` and `blob` (§2 table), the Planning source precedence, merged-ref and own-branch exclusion,
per-branch scope, batched read-only scan with the detail-read cost, and the `VIEWER_SOURCE_UNKNOWN` and
`VIEWER_SOURCE_PATH_REFUSED` refusals (§2.1), the page's overlay rules (§4.2: checkout first, in place, failure note,
ordering seed, withdrawn source, overlay cache, Proposals tab, card selection scoped to its tab), the roadmap's exclusion (§5) and the optional `planningProposals`, `planningTree` and `planningBlob`
data-source methods with the exported types (§6). Each rule names the test that enforces it.

`ADR-viewer-planning-proposal-overlay` records the decision and replaces, for proposals only, the statement of
`ADR-viewer-working-tree` §4 that the UI reads only the current checkout; that statement carries a one-line pointer as
`ADR-immutable-decisions-editable-records` prescribes for a partial replacement, and `ADR-viewer-working-tree` stays
accepted. The command reference and both package READMEs mirror the endpoints, codes, data-source methods and the
overlay behavior.

`ARCH-05-1-containers` §2.5 and `ARCH-07-deployment` still hold: the server stays foreground, loopback-only, `GET`-only
and read-only and adds no dependency, so no architecture document changes. No use case covers the viewer, no domain
term was introduced and no work is deferred. The spec carries no source feedback.

The implementation added `SddViewer`'s knowledge request so a Dashboard card opens its proposal in the Proposals tab;
it lives in `packages/devkit-viewer/frontend/src/lib/SddViewer.svelte`, inside Task 2.3's boundary.

Entrypoint derivation proposed only `packages/devkit-viewer/tests` as a new candidate for `CAP-VIEW-repository-viewer`;
it was rejected because tests verify rather than open the capability. The existing package and library entrypoints
already cover the new reader and the overlay modules.
