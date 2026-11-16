---
id: SPEC-viewer-internal-simplification
title: 'Viewer as an internal tool: drop the library surface and trim unused features'
summary: autohub no longer vendors the viewer library, so remove the npm library surface and generic-host fallbacks and trim viewer features nothing in the repository uses.
status: completed
created: 2026-11-16
related_capabilities: [CAP-VIEW-repository-viewer]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-viewer-internal-simplification] Viewer as an internal tool: drop the library surface and trim unused features

## 1. Problem Statement & Motivation

Handed off from proposal PROP-viewer-internal-simplification on 2026-11-16.
- **Preserved Materials**: `docs/materials/2026-11/20261116-viewer-internal-simplification`

`ADR-repository-viewer` built the viewer as one Svelte source with two hosts: devkit's local server and autohub's
SvelteKit UI, which vendored an `npm pack` tarball of the component library. autohub now builds its own viewer and
no longer consumes the library. The viewer remains this repository's internal Living Spec browser, served by
`devkit viewer serve`. `ADR-internal-repository-viewer` records the decision this spec delivers.

Every accommodation that exists only for a foreign host can go, and several features sized for a remote host or for
retired producers can be trimmed without losing what the repository uses: the Read tab with the handbook and the
Living Spec book, Proposals and Specs, the roadmap, the dashboard, formal references, supersession, the file
explorer and Mermaid.

Planning verified the inventory; the counts, paths and corrections to the draft audit are in
[planning evidence](../../../docs/materials/2026-11/20261116-viewer-internal-simplification/planning-evidence.md).

Accommodations that exist only for the external host:

- npm library packaging: `frontend/package.json` `files`, `svelte`, `types`, `exports`, the `package` script,
  `peerDependencies.svelte` and `@sveltejs/package`; the `pack` action and its tarball check in `scripts/viewer.sh`;
  the CI pack step; `just viewer pack` in the `FRONTEND_CHECK` line of `scripts/affected_tests.py`; and the two
  devkit tests that expect them. The `justfile` names `pack` only in a comment.
- The library barrel `frontend/src/lib/index.ts`, its one-line shims and wrappers, and the `lib/`/`app/` split.
- The optional `RepositoryDataSource` members that the local server always provides (`treeRecursive`,
  `dashboardList`, `planningProposals`, `planningTree`, `planningBlob`) and `refs?`, which nothing provides or calls;
  the discovery path for a source without `dashboardList` and its six-worker pumps; and the `ref` argument, which the
  server ignores.
- Host props and events: the `initialView`/`initialPath` book deep links, `sdd:path-change`, `sdd:item-selected` and
  the bindable `bookRequested`. The local app sets only `initialView="dashboard"` and keeps only the repository in its
  URL.
- The contract text written for a library consumer: `CAP-VIEW-repository-viewer` §6 and its library-host fallback
  clauses, `ARCH-05-1-containers`, `ARCH-07-deployment`, the package and frontend READMEs, the viewer reference,
  `setup.md` and `ci-cd.md`.

Features trimmed because no producer or need remains: the Shared tab and the `/review/<repo>/<generation>` page with
the shared API; dashboard body paging with its caches; and the Planning-overlay remote-tracking source, overlay cache,
order seeding and withdrawn-source reconciliation.

Kept regardless: the wheel that ships the committed static build and the `viewer-assets` generated artifact (they let
a Git install run without Node), the `devkit.commands` entry point, the loopback-only and GET-only server guards,
`--scan` with the repository picker, the Mermaid fullscreen modal, the 30-second document-index and roadmap reuse,
and the frontend lint, check, test, build and probe checks.

## 2. User Stories

- **US-1**: As a maintainer, I want the viewer to carry no library packaging or generic-host code so that a viewer
  change touches one host, one data-source shape and one source tree.
- **US-2**: As a reader of the Living Spec, I want the dashboard to show every open milestone, active proposal and
  open feedback entry at once, with Refresh as the only reload control, so that I never page through cards.
- **US-3**: As a reader of proposals under Planning, I want the dashboard and Proposals tab to overlay the Planning
  copy from this machine's worktrees and local branches so that I see current edits without remote or cached state.
- **US-4**: As a maintainer, I want the viewer contract, ADRs and development documents to describe only the internal
  viewer so that no clause promises a host, route or feature that no longer exists.

## 3. Non-Goals

1. **Scope Excluded**: Removing the committed static build, the `viewer-assets` generated artifact, the
   `devkit.commands` entry point or the `build:app` script name; `.devkit/generated.toml` does not change.
2. **Scope Excluded**: Changing `devkit shared` or the MCP shared tools; they remain the way to read a
   `proposal-review` artifact.
3. **Scope Excluded**: Removing `--scan`, repeated `--repo`, the repository picker or the Mermaid fullscreen modal,
   or restricting the Mermaid diagram types.
4. **Scope Excluded**: Changing the 30-second document-index and roadmap reuse in `api/cache.ts`, the server's
   loopback, Host, GET-only and path guards, or any document kind, identity or relation semantics.
5. **Scope Excluded**: Rewriting completed specs or `docs/materials/`, which keep their historical paths.
6. **Scope Excluded**: Any new viewer feature, route or data-source member.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The npm library surface is gone
- **Given** `packages/devkit-viewer/frontend/package.json`, `scripts/viewer.sh`, `.github/workflows/ci.yml` and
  `scripts/affected_tests.py`
- **When** they are read and `bash scripts/viewer.sh pack` runs with dependencies installed
- **Then** `package.json` has no `files`, `svelte`, `types`, `exports`, `peerDependencies` or `package` script and no
  `@sveltejs/package` dependency, `viewer.sh pack` exits `2` with `Unknown action: pack` on stderr, no CI step runs
  `just viewer pack`, and the `[FRONTEND_CHECK: ...]` line is
  `just viewer install && just viewer lint && just viewer check && just viewer test && just viewer build`

### [AC-02] One data source with required members
- **Given** the frontend source tree
- **When** `just viewer check` runs and the frontend is searched
- **Then** the check exits `0`; `RepositoryDataSource` declares `info`, `tree`, `treeRecursive`, `blob`,
  `dashboardList`, `planningProposals`, `planningTree` and `planningBlob` as required members and no `refs`,
  `sharedList` or `sharedBlob`; `tree`, `treeRecursive`, `blob` and `dashboardList` take no `ref` argument; and no
  source file tests a data-source member for presence or keeps a dashboard discovery path for a source without
  `dashboardList`

### [AC-03] One application source tree
- **Given** `packages/devkit-viewer/frontend/src/`
- **When** it is listed and `just viewer test` and `just viewer build` run
- **Then** no `src/lib/` or `src/app/` directory and no re-export barrel, one-line shim or wrapper component exists,
  both commands exit `0`, and
  `rg -n 'frontend/src/(lib|app)/' docs --glob '!docs/materials/**' --glob '!docs/proposals/**' --glob '!docs/decisions/2026-11/20261102-repository-viewer.md'`
  prints nothing

### [AC-04] The review page and shared API answer not found
- **Given** a running viewer serving a registered repository `repo`
- **When** a client requests `GET /review/repo/<32 hex>`, `GET /api/repos/repo/shared` or
  `GET /api/repos/repo/shared?generation=<32 hex>`
- **Then** each answers `404` with error code `VIEWER_NOT_FOUND`, no `VIEWER_REVIEW_*` or `VIEWER_SHARED_*` code
  remains in the viewer package, and the viewer sources import nothing from `devkit_dist.features.shared`

### [AC-05] No Shared tab
- **Given** the page is open on a repository
- **When** the navigation rail renders
- **Then** it offers Dashboard, Read, Proposals, Specs, the roadmap and the file explorer and no Shared entry

### [AC-06] The dashboard shows every eligible card
- **Given** a repository with more eligible entries in a section than the former page size (7 milestones, 10 active
  proposals or 7 open feedback entries)
- **When** the Dashboard opens
- **Then** each section lists frontmatter through `dashboardList` once, reads the body of every eligible entry, and
  renders all of them in the kept order (milestones active then planned; proposals review, draft then accepted; open
  feedback by critical, blocked, workaround then friction and then unknown severities; then ID, then path), and no
  Load more or per-page Retry control exists

### [AC-07] A failed body read keeps the other cards
- **Given** a dashboard section in which one eligible entry's body read rejects
- **When** the section finishes loading
- **Then** it renders the cards that read successfully, shows that entry's path with its error, and its count
  includes the failed entry

### [AC-08] Refresh reloads; tab reuse stays
- **Given** a loaded Dashboard
- **When** Refresh is selected
- **Then** the source's caches are cleared and every section lists and reads again; and a document index or roadmap
  completed within the last 30 seconds is still reused when a tab switch reopens it

### [AC-09] Planning sources are this machine's worktrees and local branches
- **Given** a repository with Planning work on `plan-<slug>` in another worktree, in a local branch, in a local branch
  merged into `HEAD`, and only in a remote-tracking ref
- **When** `GET /api/repos/<id>/planning-proposals` runs
- **Then** for each slug the worktree wins over the local branch, a merged local branch contributes no source, a
  remote-tracking ref contributes no source and no source has kind `remote`, and source-scoped `tree` and `blob`
  keep `404 VIEWER_SOURCE_UNKNOWN` and `400 VIEWER_SOURCE_PATH_REFUSED`

### [AC-10] The overlay is asked for on each load and never cached
- **Given** the Dashboard proposal section or the Proposals tab on a source
- **When** it loads, is left and loads again within 30 seconds
- **Then** each load requests `planningProposals` again, the checkout's cards render without waiting for it, the
  overlay updates matching cards in place and appends Planning-only active proposals, and a list build takes its
  order and membership from the checkout only

### [AC-11] No host props or events
- **Given** the frontend source tree and the local page
- **When** the sources are searched and the page opens
- **Then** no source contains `sdd:path-change`, `sdd:item-selected`, `initialView`, `initialPath` or a bindable
  `bookRequested` prop; the page opens on the Dashboard, the URL hash holds only the repository, and the Read tab's
  view id is `book`

### [AC-12] Generated assets and records are current
- **Given** the frontend change is committed with its rebuilt static build
- **When** `uv run devkit generated check viewer-assets` and `uv run devkit rules check --ci` run
- **Then** both exit `0`; `ADR-repository-viewer` has `status: superseded` and
  `superseded_by: ADR-internal-repository-viewer`; `ADR-release-handbook` and
  `ADR-viewer-namespace-roadmap-discovery` carry their "Superseded in part by" pointers; and
  `.devkit/architecture.toml` lists no `devkit_dist.features.shared` edge for the `browse` feature

### [AC-13] No library host in the viewer documents
- **Given** the viewer's capability, use cases, architecture, development documents and package
- **When** `rg -n 'autohub|npm pack|svelte-package' docs/capabilities/viewer docs/usecases/viewer docs/architecture/ARCH-05-1-containers.md docs/architecture/ARCH-07-deployment.md docs/development/reference/viewer.md docs/development/setup.md docs/development/ci-cd.md packages/devkit-viewer --glob '!package-lock.json' --glob '!**/static/**'`
  runs
- **Then** it prints nothing

## 5. Assumptions

- The cache helpers in `api/cache.ts` keep keying entries by source and branch; the branch is a cache key, not a
  data-source argument, so removing `ref` from the data source leaves the 30-second reuse unchanged.
- The application entry and local-server helpers move to `frontend/src/main.ts`, `frontend/src/App.svelte` and
  `frontend/src/api/local.ts`; the former `lib/` tree moves to `frontend/src/` unchanged in shape.
- The roadmap keeps its shallow structural milestone discovery over `tree` and `blob`; it is the roadmap's own
  reader, not a generic-host fallback. The six-worker milestone pump stays only where the roadmap reads milestone
  bodies.
