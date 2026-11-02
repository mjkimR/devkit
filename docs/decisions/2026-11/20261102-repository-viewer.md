---
id: ADR-repository-viewer
title: Repository viewer distribution and read-only working-tree server
summary: "For viewing devkit repositories locally, we ship a devkit-viewer wheel with committed built assets and a loopback-only GET server reading the checked-out working tree plus Planning proposal overlays, to need no Node or writes, accepting committed build output and no other-branch view."
status: accepted
created_at: 2026-11-02
aliases:
  - ADR-viewer
  - ADR-viewer-distribution-and-frontend-build
  - ADR-read-only-local-server-over-git-refs
  - ADR-local-immutable-proposal-review-view
  - ADR-viewer-working-tree
  - ADR-viewer-planning-proposal-overlay
---

# [ADR-repository-viewer] Repository viewer distribution and read-only working-tree server

- **Status**: Accepted
- **Date**: 2026-11-02
- **Deciders**: @minjae
- **Involved Components/Capabilities**: `packages/devkit-viewer/` (Python package and `frontend/`),
  `.devkit/generated.toml` (`CAP-GEN-tracked-artifacts`), `CAP-VIEW-repository-viewer`, `CAP-DLV-human-interaction`,
  `CAP-INT-mcp-services`, autohub `modules/hub-ui/`

---

## 1. Context & Problem Statement

devkit owns the viewer source (decided in Backlog, `SPEC-repository-viewer`). devkit is a Python monorepo: consumers
install its distributions from Git subdirectories at a pinned commit, so `uv` builds them from source on every
install. The viewer is a Svelte 5 component that two hosts need: devkit's own local server and autohub's SvelteKit
UI. The decision chooses the distribution, where the built assets come from, and how autohub receives the component.

The viewer reads through a `RepositoryDataSource` (`info`, `tree(path, ref)`, `blob(path, ref)`). devkit's server must
provide it for several local repositories at once, stay safe as a local web server, and decide whether the viewer
takes part in approvals. `ADR-proposal-acceptance` requires an optional readable view of immutable, expiring
proposal-review reports without committing translations.

A developer needs to inspect a saved edit without committing it. The intended use is to review the current checkout,
with the current branch name as context. The registered repository root is the boundary for file reads; the local
web server protects against path traversal and does not write to repositories. Git metadata and symlinks are not
served.

A proposal under Planning is edited on its `plan-<slug>` branch, usually in a sibling worktree, so a checkout-only
view shows the copy the main checkout last merged, which can be days behind. Branch reads through `gh` were slow.
Only `docs/proposals/PROP-<slug>/` of each Planning branch is current: the rest of that branch is a stale copy of its
base. The checkout view must not wait for anything new.

---

## 2. Decision Drivers

- Installing devkit from Git never needs Node or npm network access. (ADR-viewer)
- One source for both hosts; no registry publication. (ADR-viewer)
- People who do not run the viewer do not install its assets (the lazily loaded `mermaid` alone is several MB).
  (ADR-viewer)
- One `devkit` executable (`ADR-document-system`). (ADR-viewer)
- Do not reintroduce what autohub removed in `0d8c05f`: runtime loading of an externally hosted Custom Element bundle
  named by an HTTPS URL and SHA-256 in a Git-ignored local file, downloaded at deployment build time, and published as
  a separate operation. (ADR-viewer)
- No path outside a registered repository is reachable. (ADR-viewer)
- Any branch is readable without switching a checkout or fetching. (ADR-viewer)
- No new runtime dependency where the standard library suffices. (ADR-viewer)
- No daemon (`ARCH-01-introduction-and-goals` §3.4). (ADR-viewer)
- Each approval keeps one path (`CAP-DLV-human-interaction`, `CAP-INT-mcp-services`). (ADR-viewer)
- Repositories pinning different `devkit-spec` versions are all readable. (ADR-viewer)
- Show saved uncommitted and untracked files. (ADR-viewer-working-tree)
- Keep every file read within the registered checkout. (ADR-viewer-working-tree)
- Remove ordinary Git object reads and other-branch enumeration. (ADR-viewer-working-tree)
- Preserve the loopback-only, GET-only, no-CORS, no-write server. (ADR-viewer-working-tree)
- Keep the Python and Svelte packaging and their runtime dependencies unchanged. (ADR-viewer-working-tree)
- Show the Planning version of each proposal, including saved uncommitted and untracked files in its worktree.
  (ADR-viewer-planning-proposal-overlay)
- Keep the checkout's cards as fast as today; a slow or failed Planning read must not block or break them.
  (ADR-viewer-planning-proposal-overlay)
- Read only what is current: one proposal directory per Planning branch. (ADR-viewer-planning-proposal-overlay)
- No network, `gh`, fetch or write; no arbitrary revision reaches Git. (ADR-viewer-planning-proposal-overlay)
- Bounded Git cost per page load, independent of the number of files. (ADR-viewer-planning-proposal-overlay)

---

## 3. Considered Options

### Distribution

- **Inside `devkit-spec`, behind an extra** (rejected in `ADR-viewer-distribution-and-frontend-build`): an extra adds
  dependencies only, so the built assets would ship in every `devkit-spec` install.
- **`devkit-catalog`** (rejected in `ADR-viewer-distribution-and-frontend-build`): holds data-only content bundles;
  runtime Python code belongs elsewhere (`MS-catalog-and-context-scaling` non-goals).
- **A separate `devkit-viewer` distribution** (selected in `ADR-viewer-distribution-and-frontend-build`): mounted
  through `devkit.commands`, installed only by those who run it; needs no `devkit-spec` code, because the browser
  parses the documents.

### Built assets

- **Build at wheel build time** (rejected in `ADR-viewer-distribution-and-frontend-build`): every Git install would
  need Node and npm network access.
- **Download a release artifact at run time** (rejected in `ADR-viewer-distribution-and-frontend-build`): a
  publication step and network access at run time.
- **Commit the built assets as a tracked generated artifact** (selected in
  `ADR-viewer-distribution-and-frontend-build`): `devkit generated check` refuses stale assets; Node is needed only to
  change the frontend.

### autohub consumption

- **npm registry** (rejected in `ADR-viewer-distribution-and-frontend-build`): no publication.
- **`git+https` dependency** (rejected in `ADR-viewer-distribution-and-frontend-build`): npm installs only a
  repository's root package, and the viewer lives in a subdirectory.
- **Runtime-loaded Custom Element bundle** (rejected in `ADR-viewer-distribution-and-frontend-build`): what autohub
  removed in `0d8c05f`.
- **Vendored `npm pack` tarball** (selected in `ADR-viewer-distribution-and-frontend-build`): compiled into autohub's
  own build, so none of the removed runtime-loading machinery returns.

### Reads

- **Working tree files** (rejected in `ADR-read-only-local-server-over-git-refs`; selected in
  `ADR-viewer-working-tree` as reading saved working-tree files and showing the checked-out branch): saved uncommitted
  and untracked files appear immediately; ordinary tree and blob reads spawn no Git processes; the interface
  identifies the checkout being read; other branches and unsaved editor buffers are unavailable, and filesystem
  traversal needs explicit path and symlink checks.
- **Git objects at a ref** (selected in `ADR-read-only-local-server-over-git-refs`; rejected in
  `ADR-viewer-working-tree` as continuing to read Git objects at selected refs): `git ls-tree` and `git cat-file` reach
  only paths in the ref's tree, read any local branch, and never touch a checkout; hides saved uncommitted content,
  requires repeated Git calls and exposes branch switching that this viewer does not need.
- **An exact generation route for proposal-review artifacts through the local shared adapter** (added in
  `ADR-local-immutable-proposal-review-view`).

### Planning proposals

- **Overlay proposals from local Planning sources after the checkout** (selected in
  `ADR-viewer-planning-proposal-overlay`): a separate request enumerates `plan-*` worktrees, local branches and
  remote-tracking refs, reads only `docs/proposals/PROP-<slug>/proposal.md` of each, and the page updates matching
  cards in place; current proposals without switching checkouts, one batched Git read per scan; a remote-tracking copy
  is only as current as the last fetch, and a second source of content needs a badge.
- **Read proposals through `gh` or the pull request** (rejected in `ADR-viewer-planning-proposal-overlay`): always
  current with the remote; network latency per file, authentication, and the slowness that removed branch reads
  before.
- **Keep the checkout only** (rejected in `ADR-viewer-planning-proposal-overlay`): no new code or Git use; proposals
  under Planning stay stale.

### Server stack

- **Starlette or a similar framework** (rejected in `ADR-read-only-local-server-over-git-refs`): new dependencies for
  a GET-only local server.
- **Standard library `http.server`** (selected in `ADR-read-only-local-server-over-git-refs`): `ThreadingHTTPServer`
  with GET handlers.

### Registration

- **A user-level configuration file** (rejected in `ADR-read-only-local-server-over-git-refs`): a new file format to
  maintain.
- **Command options** (selected in `ADR-read-only-local-server-over-git-refs`).

### Parsing

- **Run each repository's `devkit spec list --format json`** (rejected in `ADR-read-only-local-server-over-git-refs`):
  needs each repository's own environment.
- **Parse in the browser, as autohub does** (selected in `ADR-read-only-local-server-over-git-refs`).

### Approvals

- **Record answers from the viewer** (rejected in `ADR-read-only-local-server-over-git-refs`): allowed for `record`
  answers by `CAP-DLV-human-interaction` §1, but the waiting agent sees them only at its next `devkit workflow next`,
  and the server would need write access, a committer and a token.
- **Grant integration approval from the viewer** (rejected in `ADR-read-only-local-server-over-git-refs`): the
  `integration_integrate` authority is bound to a request in the memory of the stdio MCP process the host started.
- **Read-only, approvals out** (selected in `ADR-read-only-local-server-over-git-refs`).

---

## 4. Decision Outcome

### Distribution and frontend

- **Python**: `packages/devkit-viewer/`, distribution `devkit-viewer`, import package `devkit_viewer`, depending on
  `devkit-agt` for `devkit_dist.adapters.cli`. Entry point `devkit.commands` `viewer`; the command is
  `devkit viewer serve`. (ADR-viewer-distribution-and-frontend-build)
- **Frontend**: one npm project under `packages/devkit-viewer/frontend/` with two outputs from one source: a Svelte
  component library (`svelte-package`: the viewer moved from autohub, `SddViewer`, `KnowledgeViews`, `documents.ts`,
  the `RepositoryDataSource` interface, plus the roadmap view; `svelte` is a peer dependency), and a Vite single-page
  app that imports the library, adds the repository switcher, and builds into `src/devkit_viewer/static/`.
  (ADR-viewer-distribution-and-frontend-build)
- **Assets**: the app build output is committed and registered in `.devkit/generated.toml` as a generated artifact
  whose inputs are the frontend sources and lockfile; Development verifies that the build is reproducible from the
  lockfile before relying on `devkit generated check`. (ADR-viewer-distribution-and-frontend-build)
- **autohub**: keeps `RepositoryView`, its Git browser (`FileTreeTable`, `FileBlobViewer`) and its run and decision
  panels (`SddExecution`, `SddProposals`, `SddRunLinks`), and passes its existing GitHub-backed data source to the
  library component. It commits the `npm pack` tarball under `modules/hub-ui/vendor/`, depends on it with
  `file:vendor/<name>.tgz`, pins its integrity in `package-lock.json` and documents the source commit and rebuild
  steps, as for `vendor/api-codegen.md`. Adopting the tarball is autohub's own change, made after a devkit commit
  carries the library. (ADR-viewer-distribution-and-frontend-build)
- **Checks**: the `just` recipes gain the frontend (lint, type check, unit tests) through `scripts/`; `just smoke`
  checks that the installed wheel serves its assets. (ADR-viewer-distribution-and-frontend-build)

### Server

- **Process**: `devkit viewer serve [--repo PATH]... [--scan DIR] [--port N]` runs in the foreground until
  interrupted. `--repo` is repeatable; `--scan DIR` registers each direct child that is a Git repository with
  `.devkit/config.toml`. stdout carries one sentinel, `[VIEWER: url=<url> repos=<n>]`; refusals are advisories with
  stable codes (an unknown or duplicate repository ID, no repository registered, port in use); access logs appear only
  under `-v`. (ADR-read-only-local-server-over-git-refs)
- **Repository ID**: the directory name; two registered repositories with the same name are refused.
  (ADR-read-only-local-server-over-git-refs)
- **API**, GET only, the `tree` and `blob` shapes matching autohub's so `httpDataSource` works unchanged:
  `/api/repos`, `/api/repos/{id}/info` (the checked-out branch as `default_branch`), `/api/repos/{id}/tree?path=`,
  `/api/repos/{id}/blob?path=`. (ADR-read-only-local-server-over-git-refs)
- **Working-tree reads**: tree and blob content is read directly from the registered current working directory, and
  the checked-out branch is displayed as a label (`HEAD` for a detached checkout). Ordinary content requests ignore any
  `ref` query parameter. Directory listings omit symlinks and `.git` directories; requests for symlinks fail as
  missing paths and `.git` paths are invalid. A resolved path outside the registered root is never served.
  (ADR-viewer-working-tree)
- **Checkout scope**: apart from proposals under Planning, the UI and the roadmap read only the current checkout.
  (ADR-viewer-working-tree, ADR-viewer-planning-proposal-overlay)
- **Proposal-review route**: one exact generation route for proposal-review artifacts reads through each registered
  repository's configured local shared adapter, unchanged by the working-tree reads. No remote adapter, arbitrary
  path, write, regeneration, sweep, approval or automatic server start is added. It renders escaped Markdown source
  with source SHA, language and expiry; no report HTML or script executes. (ADR-local-immutable-proposal-review-view,
  ADR-viewer-working-tree)
- **Safety**: binds `127.0.0.1` only, refuses a request whose `Host` header is not the loopback address or `localhost`
  at the bound port (DNS rebinding), sends no CORS headers, answers GET only and has no write endpoint.
  (ADR-read-only-local-server-over-git-refs, ADR-local-immutable-proposal-review-view, ADR-viewer-working-tree)
- **Roadmap**: milestones by status (`done` and `dropped` behind a history toggle), `depends_on` order and readiness,
  and members (proposals and specs naming the milestone). (ADR-read-only-local-server-over-git-refs)
- **Out**: open workflow requests and every write. (ADR-read-only-local-server-over-git-refs)

### Planning proposal overlay

- **Sources**: a worktree on `plan-<slug>` (read from its files), else the local branch `plan-<slug>`, else a
  remote-tracking `<remote>/plan-<slug>` as of the last fetch. A ref already merged into the checkout is no source.
  Each source contributes only `docs/proposals/PROP-<slug>/`. (ADR-viewer-planning-proposal-overlay)
- **Loading**: the checkout's proposal list renders first; one independent request enumerates the sources with one
  `git worktree list` and one `git for-each-ref` and reads every branch source through one `git cat-file --batch`.
  Cards update in place, without reordering, until the next list build. (ADR-viewer-planning-proposal-overlay)
- **Identity and reads**: each overlaid entry names its source; its bundle files are read with that source, accepted
  only for paths under its own `docs/proposals/PROP-<slug>/` and only as one of the sources enumerated for the
  request. Every other read keeps ignoring source and ref selection. (ADR-viewer-planning-proposal-overlay)
- **Boundaries**: no fetch, `gh`, pull request or write; worktree reads use the checkout's path, symlink and `.git`
  guards. (ADR-viewer-planning-proposal-overlay)
- The selected overlay meets every overlay driver; the remote staleness is visible through the badge.
  (ADR-viewer-planning-proposal-overlay)

---

## 5. Consequences

- **Positive**:
  - Git installs need no Node; one source serves both hosts; the viewer never changes what an agent or a person
    approves, or where. (ADR-viewer)
  - Saved modifications and untracked files are visible without a commit. Ordinary content reads no longer start Git
    processes. One repository view corresponds to one checked-out directory. (ADR-viewer-working-tree)
  - The Dashboard and Proposals tab show the proposal being planned, with its materials, without a branch switch. The
    checkout view is unchanged when no Planning source exists or the scan fails. (ADR-viewer-planning-proposal-overlay)
- **Negative / Risks**:
  - The repository gains its first Node toolchain, for frontend contributors only. The library's props and
    `RepositoryDataSource` become an interface autohub depends on; the vendored tarball pins a commit, so a breaking
    change reaches autohub only when it refreshes the tarball, and the release note of such a change names it.
    Refreshing the tarball in autohub is a manual step, documented beside the tarball. (ADR-viewer)
  - Other local branches are not visible. Unsaved editor buffers are unavailable. Filesystem access can race with
    changes made while a response is being assembled. (ADR-viewer-working-tree)
  - Each Planning scan starts up to three Git processes, and each source-scoped `tree` or `blob` read of an overlaid
    bundle up to three more. A remote-tracking source can be stale. Two views of one proposal exist, separated only by
    the badge. (ADR-viewer-planning-proposal-overlay)
- **Proposal reviews**: the viewer imports the shared local read contract in addition to core/advisory. Reading never
  extends TTL and expired reports require Host publication. Rendering is deliberately a readable source view;
  host-specific links and native form presentation require separate observation.
  (ADR-local-immutable-proposal-review-view)
- **Follow-ups**:
  - `AGENTS.md` and the README list the distribution, and the layering test covers `devkit_viewer`. (ADR-viewer)
  - Reconsider filesystem watchers only if users need automatic updates before navigating or reloading.
    (ADR-viewer-working-tree)
  - Extend the overlay to specs under Development only if dev worktrees show the same staleness.
    (ADR-viewer-planning-proposal-overlay)

---

## 6. Confirmation

- `devkit generated check` for the committed viewer assets; `just smoke` serves the installed wheel's assets.
  (ADR-viewer)
- The viewer frontend recipes (`just viewer lint`, `just viewer check`, `just viewer test`, `just viewer build`).
  (ADR-viewer)
- The layering test covering `devkit_viewer`. (ADR-viewer)
- Integration tests prove uncommitted and untracked files are visible and external symlinks are not served.
  (ADR-viewer-working-tree)
- Frontend tests prove the branch is a label, no selector is present, and views do not request other branches.
  (ADR-viewer-working-tree)
- `packages/devkit-viewer/tests/integration/features/browse/test_planning.py` proves precedence, per-branch scope,
  the batched read-only Git use and source refusals on real repositories. (ADR-viewer-planning-proposal-overlay)
- `packages/devkit-viewer/frontend/src/lib/features/dashboard/DashboardView.test.ts` and
  `packages/devkit-viewer/frontend/src/lib/features/knowledge/KnowledgeViews.test.ts` prove the checkout-first,
  in-place overlay and same-source bundle reads. (ADR-viewer-planning-proposal-overlay)
