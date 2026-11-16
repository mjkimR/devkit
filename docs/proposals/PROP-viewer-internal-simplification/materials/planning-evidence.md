# Planning evidence: viewer internal simplification

Verified at `plan-viewer-internal-simplification` HEAD `3fa5d0120`. Since `b0b4e2a09`, no viewer path, `scripts/viewer.sh`,
`.github/`, `justfile`, `scripts/affected_tests.py`, CAP-VIEW or ADR path has changed. The counts come from static
`rg` and `wc` runs. No test or build ran. The `scout-01` envelope holds the detailed findings.

## Library surface

| Item | Location | Note |
| --- | --- | --- |
| npm packaging | `frontend/package.json` `files`, `svelte`, `types`, `exports`, `scripts.package`, `peerDependencies`, devDependency `@sveltejs/package` | `version` 0.1.0 is stale beside the wheel's 0.1.6. It goes with `pack`. |
| Pack action and tarball checks | `scripts/viewer.sh` usage 12-14, action 56-81 | |
| CI pack step | `.github/workflows/ci.yml:85` | |
| Affected-test check line | `scripts/affected_tests.py:129` | The hard-coded expectation is in `packages/devkit/tests/e2e/package/test_affected_tests.py:348-378`. |
| Script test | `packages/devkit/tests/integration/package/test_viewer_script.py:14-24` | Parametrizes `pack`. |
| justfile | `justfile:72` | Comment only. |
| Barrel and shims | `frontend/src/lib/index.ts` (23 lines). One-line `lib/repository.ts`, `lib/documents.ts` and `lib/roadmap.ts`. Wrappers `lib/KnowledgeViews.svelte` and `lib/RoadmapView.svelte`. | `SddViewer` uses the wrappers. |
| `lib/` vs `app/` | `app/` imports only `SddViewer.svelte` and the repository shim | `lib/` has 9,445 source and 4,991 test lines. |

## Generic-host fallbacks and host surface

- `RepositoryDataSource` (`frontend/src/lib/api/repository.ts:68-127`) has the optional members `treeRecursive?`,
  `dashboardList?`, `planningProposals?`, `planningTree?`, `planningBlob?`, `sharedList?`, `sharedBlob?` and
  `refs?`. `httpDataSource` provides all of them except `refs?`, and nothing calls `refs`.
- The dashboard fallback for a source without `dashboardList` is `loadDashboardSection` (`loading.ts:21-59,
  119-137`), with the six-worker pumps in `api/documents.ts:92` and `api/milestones.ts:69`.
- The server ignores `ref` (`server.py:15`). Sixteen frontend call sites in seven files still pass it.
- The local app passes only `initialView="dashboard"` (`app/App.svelte:57-63`) and keeps only the repository in the
  URL hash (`app/api.ts:24-30`). Only tests listen for `sdd:path-change` and `sdd:item-selected`
  (`SddViewer.svelte:342-352, 504-509`). `ADR-release-handbook` states that the book deep links serve library hosts
  only.

## Trim candidates

| Candidate | Source | Tests | Note |
| --- | --- | --- | --- |
| Shared tab | `features/shared/SharedArtifactsView.svelte` (1,038 lines), rail entry, `SddViewer` view wiring, repository types | `SharedArtifactsView.test.ts` (255 lines) | |
| `/review` page and shared API | `usecases/review.py`, `usecases/shared.py`, `repositories/shared_space.py` (156 lines), `server.py:173-221` | `test_server.py:240-420`, `test_imports.py:16-23` | Codes `VIEWER_REVIEW_*` and `VIEWER_SHARED_*` occur only here. These are the viewer's only `devkit_dist.features.shared` imports. |
| Dashboard paging and caches | `loading.ts` (219 lines), page sizes 61-65, page queue 170-218, Load more and Retry in `DashboardView.svelte` | `loading.test.ts` (403 lines), parts of `DashboardView.test.ts` | About 320 directly attributable lines, not 600-900. `api/cache.ts` (55 lines) also serves the document index, roadmap and overlay. |
| Overlay extras | `repositories/planning.py` remote-tracking parse and precedence (123-126); `api/planning.ts` cache and order seeding; `loading.ts:138-150` | `test_planning.py`, `planning.test.ts` | Merged-ref exclusion is `--no-merged=HEAD` (`planning.py:106`), a filter on the single `for-each-ref`. |

Since `5d2efdefd`, no workflow in the repository produces `proposal-review` artifacts. `devkit shared put` and the MCP
`shared_put` still accept the kind, and `devkit shared get`/`list` still read it, so the viewer page is not the only
reader.

## Small optional items

| Item | Evidence | Decision |
| --- | --- | --- |
| `--scan` and the repo picker | Local multi-repository serving (`register.py:38-79`, `App.svelte:42-64`). Not specific to a foreign host. | Keep. |
| Mermaid fullscreen modal | Local reading aid (`FullscreenDiagramModal.svelte`, 201 lines). Not specific to a foreign host. | Keep. |
| Restricting Mermaid diagram types | Mermaid is imported lazily (`mermaid.ts:13`), so the 5.5 MB build affects wheel size, not page load. A restriction can leave a document's diagram unrendered. | No change. |

## Documents to change

CAP-VIEW 19-21, 114, §4.1 (129-139), §4.2 (140-170), 208-231, §6 (350-376) and the review page (377-390).
`ADR-repository-viewer` is superseded whole. The clauses superseded in part are `ADR-release-handbook` 67-69 and
190-200, `ADR-viewer-namespace-roadmap-discovery` 45-53 and `ADR-proposal-acceptance` 253-256.
`ADR-viewer-indexed-decision-supersession` mentions hosts only in its drivers and consequences, so it needs a
reference repair only (its Confirmation path). Other files: `ARCH-05-1-containers` 34, 65 and 151-160;
`ARCH-07-deployment` 21 and 102; `docs/development/reference/viewer.md` 62-110; `docs/development/setup.md` 42-50;
`docs/development/ci-cd.md` 28-29, 119-132; `packages/devkit-viewer/README.md`; `frontend/README.md`.
`UC-read-formal-document` and `UC-read-decision-supersession` cite `frontend/src/lib/` test paths.
