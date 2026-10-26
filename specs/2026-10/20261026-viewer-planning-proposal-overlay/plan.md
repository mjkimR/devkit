---
id: PLAN-viewer-planning-proposal-overlay
spec: SPEC-viewer-planning-proposal-overlay
---

# Technical Plan: `SPEC-viewer-planning-proposal-overlay` Viewer overlay of Planning proposals

## 1. Constitution & Invariant Review

- `ADR-viewer-working-tree` decides that the UI reads only the current checkout and that other branches are not
  enumerated. The overlay changes that decision for proposals only, so the new `ADR-viewer-planning-proposal-overlay`
  replaces that part, names it in its outcome, and the earlier ADR's statement gets a one-line pointer
  (`ADR-immutable-decisions-editable-records`). Every other working-tree statement stays.
- `CAP-VIEW-repository-viewer` §2 ("No ordinary content request starts Git or selects another branch"), §3 (no write,
  no fetch), §4 and §4.1 change; §5 (roadmap source) stays and gains a note that the overlay does not apply.
- No `docs/architecture/` invariant changes: the server stays loopback-only, `GET`-only and read-only, and adds no
  dependency (`ARCH-05-1-containers` §2.5).

## 2. Architecture Overview & Impact

| Component | Change |
| --- | --- |
| `features/browse/repositories/planning.py` (new) | Enumerate Planning sources; batched proposal reads; source-scoped `tree` and `blob` |
| `features/browse/usecases/read.py` | `planning-proposals` endpoint; `source` on `tree` and `blob` |
| `features/browse/http/server.py` | Pass the `source` query value; docstring of the API |
| `features/browse/models/errors.py` | `source_unknown`, `source_path_refused` |
| `frontend/src/lib/api/repository.ts` | Optional `planningProposals`, `planningTree`, `planningBlob`; types |
| `frontend/src/lib/api/planning.ts` (new) | Overlay load, cache, last-applied seed, source-scoped bundle scan |
| `frontend/src/lib/api/cache.ts` | `isCurrentGeneration` for generation-guarded seed writes |
| `features/dashboard/loading.ts` | Merge the seed into the proposals list; seeded bodies skip `blob` |
| `features/dashboard/DashboardView.svelte` | Separate overlay request; in-place display; badge; note |
| `features/knowledge/*` | Overlay in the Proposals list, source-scoped bundle, badge, no checkout "View raw" |
| `SddViewer.svelte` | Dashboard card selection reaches the Proposals tab |

No new runtime dependency.

## 3. Component & Interface Design

```mermaid
sequenceDiagram
    participant D as DashboardView
    participant S as Server
    participant G as Git / worktrees
    D->>S: dashboard-list?path=proposals (unchanged)
    D->>S: planning-proposals (independent)
    S-->>D: checkout headers -> cards render (seeded by the last overlay)
    S->>G: worktree list --porcelain; for-each-ref plan refs; cat-file --batch
    S-->>D: {sources, items, errors} -> cards update in place
```

```python
@dataclass(frozen=True)
class PlanningSource:
    id: str          # "worktree:plan-<slug>" | "branch:plan-<slug>" | "remote:<remote>/plan-<slug>"
    kind: str        # "worktree" | "branch" | "remote"
    label: str       # "worktree plan-<slug>" | "plan-<slug>" | "<remote>/plan-<slug>"
    slug: str
    commit: str      # enumerated object name; "" for a worktree
    worktree: Path | None

def planning_sources(root: Path) -> tuple[list[PlanningSource], list[str]]  # winners, errors
def planning_proposals(root: Path) -> dict[str, object]  # {"sources", "items", "errors"}
def source_tree(root, source_id, path, *, recursive) -> list[TreeItem]
def source_blob(root, source_id, path) -> bytes
```

HTTP (all `GET`):

| Endpoint | Answer |
| --- | --- |
| `planning-proposals` | `{"sources": [{"id", "kind", "label", "slug"}], "items": [{"source", "path", "content", "encoding": "utf-8"}], "errors": []}` |
| `tree?path=&recursive=&source=` | checkout `tree` shape from the source |
| `blob?path=&source=` | checkout `blob` shape from the source |

- **Enumeration**: one `git worktree list --porcelain` and one
  `git for-each-ref --format=%(refname)%00%(objectname) refs/heads/plan-* refs/remotes/*/plan-*`. Precedence per slug:
  worktree, then local branch, then the remote-tracking ref whose remote sorts first. The checkout's own slug and the
  checkout's own worktree are excluded.
- **Scan**: a worktree's `proposal.md` is read through `WorkingTreeReader(<worktree>)`; every branch source's
  `<commit>:docs/proposals/PROP-<slug>/proposal.md` goes through one `git cat-file --batch` call. Missing objects and
  non-blobs contribute no item; per-source failures go to `errors`.
- **Source reads**: `source` must equal a winning source's `id`, else `404 VIEWER_SOURCE_UNKNOWN`; the path is
  checked by `check_path`, must not hold a line break, and must be `docs/proposals/PROP-<slug>` or below it, else
  `400 VIEWER_SOURCE_PATH_REFUSED` (`VIEWER_PATH_INVALID` keeps precedence). A worktree source uses
  `WorkingTreeReader`; a branch source uses `git --literal-pathspecs ls-tree -z -l [-r -t] <commit> -- <path>/` and
  `git cat-file --batch` with `<commit>:<path>`, dropping symlinks, submodules and `.git` names. `source` is ignored by
  every other endpoint; `ref` stays ignored everywhere.
- **Frontend contract** (`RepositoryDataSource`, all optional):

```ts
planningProposals?(signal: AbortSignal): Promise<PlanningProposals>;
planningTree?(source: string, path: string, signal: AbortSignal): Promise<any>; // recursive metadata
planningBlob?(source: string, path: string, signal: AbortSignal): Promise<any>;
```

- **Overlay state** (`planning.ts`): `loadPlanningOverlay(source, ref, signal)` caches under purpose
  `planning:proposals` (30 s, generation-guarded) and records the result as the last applied overlay (a per-source
  `WeakMap`, written only while the cache generation that started the request is current). `knownOverlay(source, ref)`
  returns it. Items are accepted only when their path is `docs/proposals/PROP-<slug>/proposal.md` of their source's
  slug.
- **Dashboard**: `openDashboardPage(..., 'proposals')` merges `knownOverlay` into the list metadata (replace by path,
  add Planning-only) and stores it as `snapshot.overlay`; `nextDashboardPage` uses seeded documents instead of `blob`.
  `DashboardView` starts the overlay with the sections, in the same abortable effect; display entry for a card is
  `live[path] ?? seed[path] ?? checkout`, in snapshot order. Planning-only active entries absent from the snapshot are
  appended when no page remains, and counted. Refresh calls `clearRepositoryCache`, which also drops the cached
  overlay; the seed stays.
- **Proposals tab**: `KnowledgeViews` loads the overlay beside the index; proposal candidates use the overlay document
  for a matching path and add Planning-only ones in path order. A selected overlaid entry's bundle comes from
  `loadPlanningBundle`, a `scanDocuments` over a source-scoped data source. `ChapterSection` shows the source label in
  place of "View raw" for a sourced document; `BundleHeader` and the sidebar show the badge.
- **Dashboard navigation**: `SddViewer` passes the Dashboard's selected path as the knowledge request, so a card opens
  its proposal in the Proposals tab.

## 4. Error Handling & Edge Cases

- Git unavailable or a command failing: `planning-proposals` answers `200` with the reachable items and the failure in
  `errors`; the Dashboard shows the non-alert note.
- A worktree with a symlinked `proposal.md` or path: refused by `WorkingTreeReader`, listed in `errors`.
- A source that disappears between scan and read: `404 VIEWER_SOURCE_UNKNOWN`; the Proposals tab lists the bundle
  error like any index error.
- Planning item content that is not valid YAML: listed in the overlay errors; the checkout card stays.

## 5. Verification & Test Plan

| Scenario | Proof |
| --- | --- |
| AC-01, AC-02, AC-03 | `tests/integration/features/browse/test_planning.py`: real repository with a linked worktree, local branches and `update-ref` remote-tracking refs; `run_git` call recording |
| AC-04, AC-05 | `test_planning.py` and `test_server.py` over HTTP |
| AC-06, AC-07, AC-08 | `frontend/src/lib/features/dashboard/DashboardView.test.ts`, `loading.test.ts`, `frontend/src/lib/api/planning.test.ts` |
| AC-09 | `frontend/src/lib/features/knowledge/KnowledgeViews.test.ts`, `frontend/src/lib/SddViewer.test.ts` |
| AC-10 | existing dashboard and roadmap tests plus a no-call assertion |

Commands: `just lint devkit-viewer`, `just check devkit-viewer`, `just test-affected`, `just viewer lint`,
`just viewer check`, `just viewer test`, `just viewer build`, `uv run devkit generated check viewer-assets`,
`just rules-check`.
