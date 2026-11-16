---
id: PLAN-viewer-internal-simplification
spec: SPEC-viewer-internal-simplification
---

# Technical Plan: `SPEC-viewer-internal-simplification` Viewer as an internal tool: drop the library surface and trim unused features

## 1. Constitution & Invariant Review

- `ADR-internal-repository-viewer` (accepted at handoff) supersedes `ADR-repository-viewer` whole and, in part, the
  library-host clauses of `ADR-release-handbook` and the generic-host clauses of
  `ADR-viewer-namespace-roadmap-discovery`. Development sets `ADR-repository-viewer` to `superseded` with
  `superseded_by: ADR-internal-repository-viewer`; the two partial pointers are already in place. No further ADR is
  needed.
- `ADR-viewer-indexed-decision-supersession`, `ADR-release-handbook` and `ADR-viewer-namespace-roadmap-discovery` get
  reference repairs only: their Confirmation paths move from `frontend/src/lib/` to `frontend/src/`. No decision
  changes.
- `CAP-VIEW-repository-viewer` changes as `ADR-internal-repository-viewer` traces: §§1-2.1 (Planning sources), §4
  (tabs), §4.1 (dashboard), §4.2 (overlay), §4.3 (host deep links and location events), the library-host paragraphs
  of §4.3 and §5, §6 (library) and the review-page section.
- `ARCH-05-2-components`: the viewer drops its only `devkit_dist.features.shared` imports, so the `browse` edge to
  `devkit_dist.features.shared` leaves `.devkit/architecture.toml`. No package, feature or edge is added, and the
  `devkit-dist` public module list is unchanged.
- `CAP-GEN-tracked-artifacts`: `viewer-assets` keeps its inputs and recipe; `.devkit/generated.toml` is unchanged.

## 2. Architecture Overview & Impact

| Component | Change |
| --- | --- |
| `frontend/package.json`, `package-lock.json` | Drop `files`, `svelte`, `types`, `exports`, `scripts.package`, `peerDependencies` and devDependency `@sveltejs/package`; regenerate the lockfile with `npm install`. `build:app` keeps its name. |
| `scripts/viewer.sh`, `justfile`, `.github/workflows/ci.yml`, `scripts/affected_tests.py` | Drop the `pack` action and usage text, the recipe comment's `or pack [dir]`, the CI pack step and `just viewer pack` from `FRONTEND_CHECK`. |
| `frontend/src/` | `lib/` and `app/` collapse: `lib/<x>` moves to `src/<x>`; `app/main.ts`, `app/App.svelte`, `app/App.test.ts` move to `src/`; `app/api.ts` becomes `src/api/local.ts`. `lib/index.ts`, the shims `lib/{repository,documents,roadmap}.ts` and the wrappers `lib/{KnowledgeViews,RoadmapView}.svelte` go; `lib/{documents,roadmap}.test.ts` move to `src/api/` and `lib/RoadmapView.test.ts` to `src/features/roadmap/`. `index.html` loads `./src/main.ts`. |
| `api/repository.ts` | Required members, no `ref` argument, no `refs`, no shared members or types. |
| `api/documents.ts`, `api/milestones.ts`, `api/roadmap.ts`, `api/handbook.ts`, `api/artifacts.ts`, `api/planning.ts` | Calls lose `ref`; functions that cache keep a `branch` cache key. `scanDocuments` always lists roots with `treeRecursive`. `loadMilestoneDocuments` keeps serving the roadmap only. |
| `features/dashboard/loading.ts`, `DashboardView.svelte` | One `loadDashboardSection(source, section, signal)`: list through `dashboardList`, read every eligible body with six workers, return `{documents, errors, total}`. No page sizes, snapshots, page cache, overlay seed or fallback. Load more and Retry go. |
| `api/planning.ts`, `KnowledgeViews.svelte`, `DashboardView.svelte` | `loadPlanningOverlay(source, signal)` asks every time: no cache, no `applied` map, no presence checks. Withdrawn-source reconciliation goes. |
| `features/shared/`, `NavigationRail.svelte`, `SddViewer.svelte` | Shared tab, its view id and wiring go. |
| `SddViewer.svelte`, `KnowledgeViews.svelte`, `App.svelte` | `initialView`, `initialPath`, `sdd:path-change`, `sdd:item-selected` and the bindable `bookRequested` go; the book request stays internal to `SddViewer` and reaches `KnowledgeViews` as a plain prop with an `onBookRequest` callback. |
| `devkit_viewer.features.browse` | `http/server.py` drops `/review` and the `shared` endpoint; `usecases/review.py`, `usecases/shared.py`, `repositories/shared_space.py` and the `VIEWER_REVIEW_*`/`VIEWER_SHARED_*` errors go; `repositories/planning.py` drops remote-tracking refs. |
| `.devkit/architecture.toml` | `feature_dependencies.browse = ["devkit_dist.features.project"]`. |
| `src/devkit_viewer/static/` | Rebuilt by `devkit generated regen viewer-assets`. |
| Documents | CAP-VIEW, the two viewer use cases' `entrypoints`, `ARCH-05-1-containers`, `ARCH-07-deployment`, the ADR status and Confirmation paths, `docs/development/reference/viewer.md`, `setup.md`, `ci-cd.md`, the package and frontend READMEs. |

No new dependency is added; `@sveltejs/package` is removed.

## 3. Component & Interface Design

```ts
export interface RepositoryDataSource {
	info(signal: AbortSignal): Promise<any>;
	tree(path: string, signal: AbortSignal): Promise<any>;
	treeRecursive(path: string, signal: AbortSignal): Promise<any>;
	blob(path: string, signal: AbortSignal): Promise<any>;
	dashboardList(section: string, signal: AbortSignal): Promise<{ items: RepositoryBlob[]; errors: string[] }>;
	planningProposals(signal: AbortSignal): Promise<PlanningProposals>;
	planningTree(source: string, path: string, signal: AbortSignal): Promise<any>;
	planningBlob(source: string, path: string, signal: AbortSignal): Promise<any>;
}

/** Every eligible card of one section, read after one frontmatter listing. */
export async function loadDashboardSection(
	source: RepositoryDataSource,
	section: DashboardSection,
	signal: AbortSignal
): Promise<{ documents: RepositoryDocument[]; errors: string[]; failed: number }>;
```

`PlanningSource.kind` becomes `'worktree' | 'branch'`. The server's `planning_sources` reads
`git for-each-ref --no-merged=HEAD refs/heads/plan-*` only.

## 4. Storage & State Management

- `api/cache.ts` is unchanged: the document index and roadmap keep their 30-second reuse per source and branch, and
  Refresh calls `clearRepositoryCache`.
- The dashboard caches nothing of its own; it reloads on each open and on Refresh. The Planning overlay is never
  cached; each dashboard or Proposals load requests it.

## 5. Error Handling & Edge Cases

- A dashboard listing failure leaves the section in its error state with an unknown count. Body read failures add
  `path: error` lines; the section shows the successful cards and counts every eligible entry (AC-07).
- Aborted work (repository or branch change, disposal, Refresh) publishes nothing.
- A Planning overlay failure keeps the checkout cards and shows the existing non-alert note.
- Removed routes fall through to the existing handlers: `/review/...` reaches the static lookup and `shared` reaches
  `ReadRepositoryUseCase`, both answering `404 VIEWER_NOT_FOUND`.

## 6. Verification & Test Plan

| AC | Proof |
| --- | --- |
| AC-01 | `packages/devkit/tests/integration/package/test_viewer_script.py` (`pack` is an unknown action), `packages/devkit/tests/e2e/package/test_affected_tests.py` (`FRONTEND_LINE`), read of `package.json` and `ci.yml` |
| AC-02 | `just viewer check`; `rg` for `?(`/presence checks and `ref` arguments in `frontend/src` |
| AC-03 | `just viewer test`, `just viewer build`, the `rg` command of AC-03 |
| AC-04 | `tests/integration/features/browse/test_server.py`, `tests/integration/test_imports.py`, `rg 'VIEWER_(REVIEW|SHARED)_'` |
| AC-05 | `frontend/src/SddViewer.test.ts` |
| AC-06, AC-07, AC-08 | `frontend/src/features/dashboard/loading.test.ts`, `frontend/src/features/dashboard/DashboardView.test.ts`, `frontend/src/features/roadmap/RoadmapView.test.ts` |
| AC-09 | `tests/integration/features/browse/test_planning.py` |
| AC-10 | `frontend/src/api/planning.test.ts`, `DashboardView.test.ts`, `features/knowledge/KnowledgeViews.test.ts` |
| AC-11 | `frontend/src/SddViewer.test.ts`, `frontend/src/App.test.ts`, `rg` for the removed names |
| AC-12 | `uv run devkit generated check viewer-assets`, `uv run devkit rules check --ci --base 4bd757276` |
| AC-13 | the `rg` command of AC-13 |

Repository checks: `just viewer install && just viewer lint && just viewer check && just viewer test && just viewer
build`, `just lint-check`, `just test-affected --base 4bd757276` (with its `mode=full` fallback) and
`uv run devkit rules check --ci --base 4bd757276`.
