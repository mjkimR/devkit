---
reconcile_id: REC-viewer-internal-simplification
status: pending
targets:
  - file: docs/capabilities/viewer/CAP-VIEW-repository-viewer.md
    resolution: modified
  - file: docs/usecases/viewer/UC-read-decision-supersession.md
    resolution: modified
  - file: docs/usecases/viewer/UC-read-formal-document.md
    resolution: modified
  - file: docs/architecture/ARCH-05-1-containers.md
    resolution: modified
  - file: docs/architecture/ARCH-07-deployment.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-repository-viewer.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-release-handbook.md
    resolution: modified
  - file: docs/decisions/2026-11/20261104-viewer-namespace-roadmap-discovery.md
    resolution: modified
  - file: docs/decisions/2026-11/20261110-viewer-indexed-decision-supersession.md
    resolution: modified
  - file: docs/decisions/2026-11/20261116-internal-repository-viewer.md
    resolution: modified
  - file: docs/development/reference/viewer.md
    resolution: modified
  - file: docs/development/setup.md
    resolution: modified
  - file: docs/development/ci-cd.md
    resolution: modified
---

# Reconciliation: `SPEC-viewer-internal-simplification`

## Contract comparison

`ADR-internal-repository-viewer` (accepted at handoff) makes the viewer an internal tool with one host,
`devkit viewer serve`. The implementation matches it clause by clause:

- **Distribution and frontend**: `frontend/package.json` has no `files`, `svelte`, `types`, `exports`,
  `peerDependencies`, `package` script or `@sveltejs/package`; `scripts/viewer.sh` has no `pack` action (an unknown
  action exits `2`); CI runs no pack step; `FRONTEND_CHECK` is install, lint, check, test and build. The committed
  build, `viewer-assets` and `build:app` are unchanged, and `.devkit/generated.toml` did not change.
  `CAP-VIEW-repository-viewer` §6 now states the build and the data source instead of the library.
- **One source tree**: `frontend/src/lib/` and `frontend/src/app/` collapsed into `frontend/src/`; the barrel, shims
  and wrapper components are gone. The capability and use-case `entrypoints` and every Check path name the new paths;
  the Confirmation paths of `ADR-release-handbook`, `ADR-viewer-namespace-roadmap-discovery` and
  `ADR-viewer-indexed-decision-supersession` were repaired without changing a decision (the stale `just viewer pack`
  command in the namespace-roadmap Confirmation went with it). The superseded `ADR-repository-viewer` keeps its
  historical paths.
- **One data source**: every `RepositoryDataSource` member is required, `refs`, the shared members and the `ref`
  argument are gone, `scanDocuments` lists each root with one recursive request, and no presence check or dashboard
  discovery fallback remains. Stated in CAP-VIEW §6.
- **Shared tab and review page**: the rail has no Shared entry; `/review/...` and `/api/repos/<id>/shared` fall to
  the existing handlers and answer `404 VIEWER_NOT_FOUND`; no `VIEWER_REVIEW_*` or `VIEWER_SHARED_*` code remains;
  the viewer imports nothing from `devkit_dist.features.shared`, and the `browse` edge left
  `.devkit/architecture.toml`. The review-page section of CAP-VIEW is removed.
- **Dashboard**: one listing per section and every eligible body read; failed reads keep the other cards, list the
  path and count in the total; Refresh clears the caches and reloads; the document index and roadmap keep their
  30-second reuse. CAP-VIEW §4.1 restates these as All eligible cards, Ordering, Partial failure, No dashboard cache
  and Freshness.

`devkit spec entrypoints derive` proposed no pair worth writing: the capability and use-case `entrypoints` already name
`frontend/src/` paths, and the other candidates are configuration, lockfiles or READMEs.
- **Planning overlay**: sources are another worktree, else the local branch; merged local branches and
  remote-tracking refs are no source; source refusals are unchanged. The overlay is requested on every dashboard or
  Proposals load and seeds no order. CAP-VIEW §2.1 and §4.2 are updated; Ordering seed, Withdrawn source and Overlay
  cache are removed.
- **Host surface**: `initialView`, `initialPath`, `initialAnchor`, `apiBase`, `onselectpath`, the `sdd:path-change`
  and `sdd:item-selected` events, the bindable `bookRequested` and the handbook page request props are gone; the page
  opens on the Dashboard and `book` remains the Read tab's id. CAP-VIEW §4.3 drops Host deep links and Location.
- **Supersession records**: `ADR-repository-viewer` is `superseded` with `superseded_by:
  ADR-internal-repository-viewer`; the two partial pointers written at handoff stand. Its statement in the new ADR
  and the repeated pointer drop the clause that it would become superseded after handoff, and the new ADR's option
  text no longer names the proposal's Planning decisions as its origin.

`ARCH-05-1-containers` and `ARCH-07-deployment` drop the vendored library and its npm policy. The development
reference, `setup.md` and `ci-cd.md` drop the pack action and describe the dashboard and overlay as delivered; the
package and frontend READMEs (derived documents, not Living Spec targets) follow.

## Removed paths

| Removed | Replacement |
| --- | --- |
| `frontend/src/lib/<x>` | `frontend/src/<x>` |
| `frontend/src/app/{main.ts,App.svelte,App.test.ts}` | `frontend/src/` |
| `frontend/src/app/api.ts` | `frontend/src/api/local.ts` |
| `frontend/src/lib/{documents,roadmap}.test.ts` | `frontend/src/api/` |
| `frontend/src/lib/RoadmapView.test.ts` | `frontend/src/features/roadmap/RoadmapView.test.ts` |
| `frontend/src/lib/{index.ts,repository.ts,documents.ts,roadmap.ts,KnowledgeViews.svelte,RoadmapView.svelte}` | none (re-export layer) |
| `frontend/src/lib/features/shared/` | none (Shared tab removed) |
| `usecases/review.py`, `usecases/shared.py`, `repositories/shared_space.py` | none (`/review` and shared API removed) |

## Design, domain and operations

- **Design**: no formal design document covers the viewer; CAP-VIEW and `ARCH-05-1-containers` own its structure.
- **Domain**: unaffected; no document kind, identity or relation semantics changed.
- **Operations**: no operations document covers the viewer; `just viewer` lost `pack`, recorded in `setup.md` and
  `ci-cd.md`.

## Deferred work

Stale wording outside this unit's boundaries is reported to the Host as feedback, not edited here:
`UX-view-decision` host wording, `ADR-package-ownership-and-release-version`'s frontend npm library version clause,
and the decision text of `ADR-viewer-namespace-roadmap-discovery` and `ADR-viewer-indexed-decision-supersession` that
mentions library hosts, paging and caches beyond what the partial pointers cover.
