---
id: PADR-internal-repository-viewer
title: Internal single-host repository viewer
summary: "For a viewer only devkit's local server hosts, we drop the Svelte library, generic-host fallbacks and remote-host features but keep the committed-build wheel and read-only working-tree server, to cut code and contract surface, accepting that no other host can embed it."
proposal: PROP-viewer-internal-simplification
supersedes: [ADR-repository-viewer, ADR-release-handbook, ADR-viewer-namespace-roadmap-discovery, ADR-proposal-acceptance]
status: draft
created_at: 2026-11-16
---

# [PADR-internal-repository-viewer] Internal single-host repository viewer

- **Status**: Draft
- **Date**: 2026-11-16
- **Involved Components/Capabilities**: `packages/devkit-viewer/` (Python package and `frontend/`),
  `.devkit/generated.toml` (`CAP-GEN-tracked-artifacts`), `CAP-VIEW-repository-viewer`, `ARCH-05-1-containers`,
  `ARCH-07-deployment`, `scripts/viewer.sh`, `scripts/affected_tests.py`, `.github/workflows/ci.yml`

---

## 1. Context & Problem Statement

`ADR-repository-viewer` built the viewer as one Svelte source for two hosts: devkit's local server and autohub's
SvelteKit UI, which vendored an `npm pack` tarball of the component library. autohub now builds its own viewer and
consumes neither the library nor its `RepositoryDataSource` interface. The viewer remains this repository's internal
Living Spec browser, served only by `devkit viewer serve`.

Everything that exists only for a foreign host still costs code, tests, CI time and contract text: the library
packaging and its pack check, a barrel and a `lib/`/`app/` split, optional data-source members with fallback
discovery for hosts without the local endpoints, host-only props and events, and contract clauses written for a
library consumer. Several features were sized for a remote host's cold load or for producers that no longer exist:
the Shared tab and the `/review/<repo>/<generation>` page for `proposal-review` artifacts, dashboard body paging with
per-page caches, and Planning-overlay sources and caches beyond the local machine.

The committed static build is independent of autohub: it lets a Git install of `devkit-viewer` serve the page without
Node.

---

## 2. Decision Drivers

- Keep what the repository uses: Dashboard, Proposals and Specs, the Reading tab with the handbook, Files with formal
  references, supersession and Mermaid, and the roadmap.
- Installing devkit from Git still needs no Node or npm network access.
- Keep the loopback-only, GET-only, no-CORS, no-write server and its path guards.
- Remove contracts and code that no consumer in this repository exercises.
- Show the Planning version of a proposal being edited on this machine without blocking the checkout's cards.
- One host, one data-source shape: no optional member and no fallback path to keep in parity.

---

## 3. Considered Options

- **Keep the two-host design unchanged**: no work; the library contract, its fallbacks and the remote-sized features
  keep their maintenance and test cost with no consumer.
- **Remove only the library packaging and pack check**: small; the barrel, optional members, fallback discovery and
  host-only contract clauses stay as dead generality.
- **Internal single-host viewer, keeping every current feature**: removes the library surface and generic-host
  fallbacks; the Shared tab, `/review` page, dashboard paging and the full overlay stay without a producer or need.
- **Internal single-host viewer with the unused features trimmed** (selected): removes the library surface and
  fallbacks and trims the features the Planning decisions of `PROP-viewer-internal-simplification` select.
- **Drop the committed static build as well**: Git installs would need Node to build the page; rejected because the
  build exists for Git installs, not for autohub.

---

## 4. Decision Outcome

The viewer is an internal tool with one host, `devkit viewer serve`, and no published or vendored library.

### Distribution and frontend

- `packages/devkit-viewer/` ships distribution `devkit-viewer`, import package `devkit_viewer`, mounted through the
  `devkit.commands` entry point `viewer`; the command is `devkit viewer serve`. → `CAP-VIEW-repository-viewer` §1
  (MUST).
- The frontend is one Vite single-page application under `packages/devkit-viewer/frontend/`, with no
  `svelte-package` output, no package `exports`, no peer dependency and no `npm pack` tarball.
  → `CAP-VIEW-repository-viewer` §6 (MUST).
- The application build is committed under `src/devkit_viewer/static/` as a tracked generated artifact whose inputs
  are the frontend sources and lockfile, so a Git install serves the page without Node.
  → `CAP-VIEW-repository-viewer` §6 (MUST).
- The frontend checks are lint, type check, unit tests and build through `scripts/viewer.sh`; CI and
  `scripts/affected_tests.py` run no pack step. `just smoke` checks that the installed wheel serves its assets.

### Server and data source

- The server reads the registered working tree: saved, uncommitted and untracked files, with the checked-out branch
  as a label; `ref` parameters are not part of the interface. Directory listings omit symlinks and `.git`;
  a resolved path outside the registered root is never served. → `CAP-VIEW-repository-viewer` §2 (MUST).
- The server binds `127.0.0.1` only, refuses a non-loopback `Host` header, sends no CORS headers, answers GET only and
  has no write endpoint. → `CAP-VIEW-repository-viewer` §3 (MUST).
- The page uses one data source, the local HTTP API; recursive tree listing, dashboard header listing, Planning
  proposals and source-scoped Planning reads are required members, there is no `refs` member or `ref` argument, and
  the frontend keeps no discovery path for a source without them. The frontend is one application source tree without
  a `lib/` re-export layer.
  → `CAP-VIEW-repository-viewer` §2 and §4.1 (MUST).
- The viewer reads no shared artifacts: the Shared tab and the `/review/<repo>/<generation>` page are removed, and
  the viewer has no dependency on `devkit_dist` shared-artifact APIs. → `CAP-VIEW-repository-viewer` §4 (MUST).

### Dashboard

- A dashboard section lists frontmatter through `dashboard-list`, reads the bodies of its eligible entries, and shows
  all of them; there is no body paging, Load more, per-page Retry or dashboard list or page cache. Refresh clears the
  source's caches and reloads the sections. → `CAP-VIEW-repository-viewer` §4.1 (MUST).
- The document index and roadmap keep their 30-second reuse within a page, because tab switches reuse them.
  → `CAP-VIEW-repository-viewer` §4.1 (MUST).

### Planning proposal overlay

- Planning sources are another worktree on `plan-<slug>` (its saved files), else the local branch `plan-<slug>`; a
  local branch already merged into the checkout is no source. Remote-tracking refs are not read.
  → `CAP-VIEW-repository-viewer` §2.1 (MUST).
- The checkout's cards render first; the overlay arrives in a separate request and updates matching cards in place,
  appending Planning-only proposals. The overlay is not cached across visits and does not seed list order.
  → `CAP-VIEW-repository-viewer` §4.2 (MUST).
- Each overlaid entry names its source; its bundle files are read only under its own `docs/proposals/PROP-<slug>/`
  and only from a source enumerated for that request. No fetch, `gh`, pull request or write.
  → `CAP-VIEW-repository-viewer` §2.1 (MUST).

### Host surface

- The page opens on the Dashboard and keeps only the repository in its address; `initialPath` book deep links, the
  `sdd:path-change` and `sdd:item-selected` events and the bindable book request for a standalone `KnowledgeViews`
  host are removed.
  → `CAP-VIEW-repository-viewer` §4.3 (MUST).

### Supersession

Supersedes in part `ADR-repository-viewer`: every decision (distribution and frontend, autohub consumption, server, working-tree reads, proposal-review route and Planning proposal overlay); the ADR becomes superseded after handoff.

Supersedes in part `ADR-release-handbook`: the library-host clauses (library hosts keep their `RepositoryDataSource`; hosts keep the `book` view id, `initialView` and the `sdd:path-change` event; the standalone `KnowledgeViews` binding of the book request; the library-host deep links).

Supersedes in part `ADR-viewer-namespace-roadmap-discovery`: the generic-host clauses (generic discovery trusting host tree/blob representation; generic hosts keeping their tree/blob interface; one helper serving both generic routes).

Supersedes in part `ADR-proposal-acceptance`: the viewer exception permitting registered-local-adapter, exact-generation `proposal-review` artifact reads.

- Removing every foreign-host accommodation and the features without a producer meets "remove contracts and code
  no consumer exercises" while the kept list meets "keep what the repository uses"; the committed build keeps
  Node-free Git installs.

---

## 5. Consequences

- **Positive**:
  - No library contract, pack check or fallback path to keep in parity; the frontend and CAP-VIEW shrink.
  - The viewer backend no longer imports shared-artifact APIs.
  - The dashboard and overlay follow one simple path: list, read, show; Refresh reloads.
- **Negative / Risks**:
  - Any future external host must reintroduce a library build and a data-source contract.
  - A `proposal-review` artifact published through `devkit shared put` or MCP `shared_put` has no viewer page; it
    stays readable through `devkit shared` commands.
  - A Planning branch that exists only on a remote is not overlaid until it is checked out or fetched into a local
    branch.
  - A dashboard section reads every eligible body on open; the cost grows with the number of open proposals,
    milestones and open feedback entries.
- **Follow-ups**:
  - Reintroduce paging only if a measured dashboard open exceeds what a local read should take.

---

## 6. Confirmation

- `devkit generated check` for the committed viewer assets; `just smoke` serves the installed wheel's assets.
- `just viewer lint`, `just viewer check`, `just viewer test`, `just viewer build`; no `pack` action remains.
- `packages/devkit-viewer/tests/integration/features/browse/test_planning.py` proves worktree-then-local-branch
  precedence, merged-branch exclusion, no remote-tracking source and source refusals.
- `packages/devkit-viewer/tests/integration/features/browse/test_server.py` proves that `/review/...` and shared
  endpoints answer `404 VIEWER_NOT_FOUND`.
- Frontend dashboard tests prove all eligible cards render without Load more and Refresh reloads.
- `RULE-decision-supersession` checks the supersession metadata and the partial pointers.
