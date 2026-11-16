---
id: PROP-viewer-internal-simplification
title: 'Viewer as an internal tool: drop the library surface and trim unused features'
summary: autohub no longer vendors the viewer library, so remove the npm library surface and generic-host fallbacks and trim viewer features nothing in the repository uses.
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-11-16
target_area: viewer/
priority: high                        # critical | high | medium | low
size: L                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-viewer/
    - packages/devkit/tests/integration/package/test_viewer_script.py
    - packages/devkit/tests/e2e/package/test_affected_tests.py
    - docs/capabilities/viewer/
    - docs/usecases/viewer/
    - docs/architecture/ARCH-05-1-containers.md
    - docs/architecture/ARCH-07-deployment.md
    - docs/decisions/
    - docs/development/reference/viewer.md
    - docs/development/setup.md
    - docs/development/ci-cd.md
    - docs/proposals/PROP-viewer-internal-simplification/
    - scripts/viewer.sh
    - scripts/affected_tests.py
    - .github/workflows/ci.yml
    - justfile
  excludes:
    - handbook/
    - packages/devkit-dist/
    - docs/capabilities/collaboration/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-viewer-internal-simplification] Viewer as an internal tool: drop the library surface and trim unused features

## 1. Background & Hypothesis

`ADR-repository-viewer` built the viewer as one Svelte source with two hosts: devkit's local server and autohub's
SvelteKit UI, which vendored an `npm pack` tarball of the component library. autohub now builds its own viewer and
no longer consumes the library. The viewer remains this repository's internal Living Spec browser, served by
`devkit viewer`.

Hypothesis: every accommodation that exists only for a foreign host can go. Several features sized for a remote
host or for retired producers can be trimmed without losing what the repository uses: the book, proposals and
specs, the handbook, the roadmap, the dashboard, formal references, supersession, the explorer and Mermaid.

Planning verified the inventory at the worktree HEAD. The counts, paths and corrections to the draft audit are in
[planning evidence](materials/planning-evidence.md) and `envelopes/scout-01.yaml`.

Accommodations that exist only for the external host:

- npm library packaging: `frontend/package.json` `files`, `svelte`, `types`, `exports`, the `package` script,
  `peerDependencies.svelte` and `@sveltejs/package`. It also covers the `pack` action and its tarball check in
  `scripts/viewer.sh`, the CI pack step, `just viewer pack` in `scripts/affected_tests.py` and the two devkit tests
  that expect them. The `justfile` names `pack` only in a comment.
- The library barrel `frontend/src/lib/index.ts`, its one-line shims and wrappers, and the `lib/`/`app/` split.
- The optional `RepositoryDataSource` members that the local server always provides (`treeRecursive`,
  `dashboardList`, `planningProposals`, `planningTree`, `planningBlob`) and `refs?`, which nothing provides or calls.
  The no-`dashboardList` discovery path and its six-worker pumps also serve only other hosts. So does the `ref`
  parameter, which the server ignores and 16 frontend call sites still pass.
- Host props and events: the `initialView`/`initialPath` book deep links, `sdd:path-change`, `sdd:item-selected`
  and the bindable `bookRequested`. The local app sets only `initialView="dashboard"` and keeps only the repository
  in its URL.
- Documentation: CAP-VIEW §6, its autohub mentions and its library-host fallback text; `ARCH-05-1-containers` and
  `ARCH-07-deployment`; `ADR-repository-viewer`; the host clauses of `ADR-release-handbook` and
  `ADR-viewer-namespace-roadmap-discovery`; the viewer exception in `ADR-proposal-acceptance`; the package and
  frontend READMEs, the viewer reference, `setup.md` and `ci-cd.md`.

Kept regardless:

- The wheel that ships the committed static build, and the `viewer-assets` generated artifact. They let a Git
  install run without Node; they do not exist for autohub.
- The `devkit.commands` entry point.
- The loopback-only and GET-only server guards.
- The frontend lint, check, test, build and probe checks.

## 2. Technical Spike Questions

The user settled every question at the recommended option; Planning settled the remaining choices on evidence.

- **Q1** (which trims are in scope): Shared tab and `/review`, dashboard paging and caching, and the Planning-overlay
  extras are trimmed. The small optional items are decided on evidence in decision 6.
- **Q2** (`lib/` split): `frontend/src/lib` collapses into one application source tree.
- **Q3** (supersede or amend): a new decision supersedes `ADR-repository-viewer` whole and three other ADRs in part.
  In SDD, a changed decision is a new ADR with `supersedes`.
- **Q4** (deep links): removed with the host events, because the local app does not use them.
- **Q5** (split): one feature unit, size L.

## 3. Proposed Design & Impact

### Planning decisions

1. **One host** (user). The viewer has one host, `devkit viewer serve`. Development removes the npm library surface
   and its pack check from `scripts/viewer.sh`, CI, `scripts/affected_tests.py` and the two devkit tests. It removes
   the barrel, shims and wrappers. The members of `RepositoryDataSource` that the local server serves become
   required. `refs?`, the no-`dashboardList` discovery path and the `ref` parameter go. The committed static build,
   `viewer-assets` and the `build:app` script name stay, so `.devkit/generated.toml` does not change.
2. **Shared tab and `/review` removed** (user). Development removes `SharedArtifactsView` and its rail entry and view
   wiring. It also removes the shared repository types and members, the `/review/<repo>/<generation>` and shared API
   routes, `usecases/review.py`, `usecases/shared.py`, `repositories/shared_space.py`, the `VIEWER_REVIEW_*` and
   `VIEWER_SHARED_*` codes and their tests. The `devkit_dist` shared allowance goes from `test_imports.py`. Removed
   paths answer `404 VIEWER_NOT_FOUND`, like any unknown endpoint. `devkit shared` and the MCP shared tools are
   unchanged and remain the way to read a `proposal-review` artifact.
3. **Dashboard: list, read, Refresh** (user). A section lists frontmatter through `dashboard-list`, reads the bodies
   of every eligible entry and shows them all in the existing order. The 6/9/6 pages, Load more, per-page Retry, the
   dashboard list and page caches and order seeding all go. Sections still load independently, show loading and
   error states, and drop work after disposal. Refresh clears the source's caches and reloads. The 30-second
   document-index and roadmap reuse in `api/cache.ts` stays: it serves tab switching, not a remote cold load.
4. **Overlay: worktree and local branch** (user). The sources are another worktree on `plan-<slug>`, then the local
   branch `plan-<slug>`. Remote-tracking refs are not read. A local branch merged into the checkout stays excluded
   (`--no-merged=HEAD` on the existing `for-each-ref`), so a stale branch cannot bring back a proposal the checkout
   deleted. The overlay request, in-place card update, Planning-only append, source badges and source-scoped reads
   with their refusal codes stay. The overlay cache, order seeding and withdrawn-source reconciliation go: each
   dashboard or Proposals load asks again.
5. **Host surface removed** (user). `initialPath`, `sdd:path-change`, `sdd:item-selected` and the bindable
   `bookRequested` go. The page opens on the Dashboard as today, and the book-request state stays internal to
   `SddViewer`. The URL hash keeps only the repository.
6. **Small items on evidence** (Planning). `--scan`, repeated `--repo` and the repository picker stay: they serve
   local multi-repository use and do not exist for a foreign host. The Mermaid fullscreen modal stays as a local
   reading aid. The Mermaid diagram types stay unrestricted: Mermaid loads lazily, so a restriction would shrink only
   the wheel and could leave a document diagram unrendered.
7. **Source layout** (user). `frontend/src/lib/` collapses into the application tree under `frontend/src/`, so no
   `lib/`/`app/` split or re-export layer remains. Check paths in CAP-VIEW, the viewer use cases' `entrypoints`, and
   the Confirmation paths in `ADR-viewer-indexed-decision-supersession` are repaired to the new paths. The repairs
   leave every decision unchanged. Completed specs and `docs/materials/` keep their historical paths.
8. **Decision record** (Planning). `PADR-internal-repository-viewer` restates the retained decisions and supersedes
   `ADR-repository-viewer` whole. It also supersedes in part the library-host clauses of `ADR-release-handbook`, the
   generic-host clauses of `ADR-viewer-namespace-roadmap-discovery` and the viewer exception of
   `ADR-proposal-acceptance`. A whole replacement leaves one current viewer decision instead of an ADR full of
   partial pointers. After handoff, Development sets `ADR-repository-viewer` to `superseded` with `superseded_by` and
   adds the three partial pointers, which `RULE-decision-supersession` checks.
9. **Split** (Planning). One feature spec, size L. The work is one package and its contract and has one task kind.
   Its tasks are ordered: library and fallbacks, collapse, trims, then docs. A split would leave CAP-VIEW and the ADR
   half-updated between units. `dev_effort` stays `medium`: nothing irreversible changes, and no consumer remains.

### Development tasks (ordered)

1. Remove the library surface: `package.json` fields and `package` script, the `pack` action in
   `scripts/viewer.sh`, CI, `scripts/affected_tests.py` (`FRONTEND_CHECK`), `test_viewer_script.py`,
   `test_affected_tests.py`, and the barrel, shims and wrappers.
2. Make the local data-source members required. Remove `refs?`, the no-`dashboardList` discovery path and the `ref`
   parameter.
3. Collapse `frontend/src/lib/` into the application tree and repair test imports.
4. Remove the Shared tab, the `/review` page and the shared API, frontend and backend (decision 2).
5. Simplify dashboard loading (decision 3) and the Planning overlay (decision 4), backend and frontend.
6. Remove the host props and events (decision 5).
7. Regenerate `viewer-assets`.
8. Update the docs: CAP-VIEW §§1-6 and the review-page section, the viewer use cases' `entrypoints`,
   `ARCH-05-1-containers`, `ARCH-07-deployment`, `docs/development/reference/viewer.md`, `setup.md`, `ci-cd.md`, and
   the package and frontend READMEs. Also make the ADR status and pointer changes of decision 8.

### Design, domain and operations impact

- **Design**: no formal design document covers the viewer, so there is nothing to update. CAP-VIEW and
  `ARCH-05-1-containers` own the structure statements and change as listed.
- **Domain**: unaffected. No document kind, identity or relation semantics change; the viewer only renders them.
- **Operations**: unaffected. No operations document covers the viewer. `just viewer` loses its `pack` action, and
  `docs/development/ci-cd.md` and `setup.md` record that.
- **Architecture**: the viewer drops its `devkit_dist.features.shared` imports. No package, feature or feature edge is
  added. `.devkit/architecture.toml` is unchanged.

### Expected acceptance evidence

- **A1 Library gone**: no `exports`, `files`, `svelte`, `types`, `package` script or peer dependency remains in
  `package.json`. `scripts/viewer.sh pack` is an unknown action. CI and `FRONTEND_CHECK` run no pack.
  `rg -n 'autohub|npm pack|svelte-package' docs/capabilities docs/architecture docs/development packages/devkit-viewer`
  finds no viewer-library mention (the frontend lockfile excepted).
- **A2 One data source**: the required members type-check (`just viewer check`). No frontend file passes `ref` or
  calls a fallback discovery path. Dashboard, roadmap and overlay tests run against the required members.
- **A3 Trims**: `test_server.py` proves `/review/...` and the removed shared endpoints answer
  `404 VIEWER_NOT_FOUND`. No `VIEWER_REVIEW_*` or `VIEWER_SHARED_*` code remains. Dashboard tests prove that every
  eligible card renders without Load more and that Refresh reloads. `test_planning.py` proves the worktree-then-local
  precedence, merged-branch exclusion, no remote-tracking source, and the source refusals.
- **A4 Host surface**: the frontend contains no `sdd:path-change`, `sdd:item-selected` or `initialPath`, and the
  local app still opens on the Dashboard.
- **A5 Checks**: `just viewer lint`, `check`, `test` and `build`; `uv run devkit generated check viewer-assets`;
  `just test-affected`; and `uv run devkit rules check` pass.

## 4. Lifecycle & Retirement Criteria

- Planning settled Q1-Q5 at the recommended options. The Host asks for `plan-accept`, then hands off to one
  `sdd-spec-feature` unit, which is integrated locally under `dev-integration=auto`.
- At handoff, `PADR-internal-repository-viewer` becomes an ADR. Development then sets `ADR-repository-viewer` to
  `superseded` and adds the partial pointers in the three other ADRs.
- Retire the proposal when the trimmed viewer lands and A1-A5 hold.
