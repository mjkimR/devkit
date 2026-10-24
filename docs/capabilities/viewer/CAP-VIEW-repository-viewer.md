---
id: CAP-VIEW-repository-viewer
title: "Local Repository Viewer"
summary: "A read-only local page, served by devkit viewer serve, that shows saved working-tree files and the checked-out branch for several devkit repositories, loads dashboard sections as cached ordered lists with incremental body pages, and supplies the Svelte viewer library autohub vendors."
area: viewer
status: active
entrypoints:
  - packages/devkit-viewer/src/devkit_viewer/
  - packages/devkit-viewer/frontend/src/app/
  - packages/devkit-viewer/frontend/src/lib/
created_at: 2026-10-19
---

# [CAP-VIEW-repository-viewer] Local Repository Viewer

The `devkit-viewer` distribution gives people a screen for what agents read through `devkit spec`: the Living Spec,
proposals, specs and milestones (`ADR-roadmap-and-milestones`, `ADR-roadmap-and-milestones`). It mounts
`devkit viewer` under the `devkit` command line (`CAP-HARN-command-mount`). devkit owns the viewer's source; autohub
consumes its component library as a vendored tarball (`ADR-viewer`). The server's
choices are `ADR-viewer` as superseded by `ADR-viewer-working-tree`. Command quick reference:
[reference](../../development/reference/viewer.md).

## 1. Serving

`devkit viewer serve [--repo PATH]... [--scan DIR]... [--port N]` registers repositories, binds `127.0.0.1:<port>`
(default `8765`, `0` for any free port), prints one line and serves in the foreground until `SIGINT` or `SIGTERM`,
then exits `0`:

```text
[VIEWER: url=http://127.0.0.1:8765/ repos=3]
```

Nothing else is written to stdout. Request logs are `[INFO]` lines on stderr under `-v` only.

- **Registration**: `--repo` names the top level of a Git work tree; `--scan` adds each direct child that is such a
  top level and holds `.devkit/config.toml`; with neither, the devkit project containing the current directory is
  served. A repository's ID is its directory name.
- **Refusals** (exit `2`, before anything is served): `VIEWER_REPO_DUPLICATE` (two registered directories share a
  name), `VIEWER_REPO_INVALID` (a `--repo` that is not a Git top level), `VIEWER_NO_REPOSITORY` (nothing to serve),
  `VIEWER_PORT_IN_USE`.
- It is not a daemon (`ARCH-01-introduction-and-goals` §3.4): a person starts and stops it.

## 2. Reading the working tree

Ordinary tree and blob endpoints read saved files below the registered repository root. They include uncommitted and untracked files. A request path is repository-relative; absolute paths, `.git` segments, `.` segments, `..` segments, empty segments and backslashes are invalid. Symlinks and `.git` directories are omitted from listings and cannot be read. No ordinary content request starts Git or selects another branch.

| Endpoint (`GET`) | Answer |
| --- | --- |
| `/api/repos` | `{"repos": [{"id", "default_branch"}]}`, sorted by ID |
| `/api/repos/<id>/info` | `{"repo_id", "default_branch"}` |
| `/api/repos/<id>/tree?path=` | `{"items": [{"name", "path", "type": "tree"\|"blob", "size"?}]}`: one directory, directories first |
| `/api/repos/<id>/dashboard-list?path=<section>` | `{"items": [{"path", "content", "encoding": "utf-8"}], "errors": ["path: error"]}`: frontmatter only for `milestones`, `proposals` or `feedback` |
| `/api/repos/<id>/blob?path=` | `{"path", "encoding": "base64", "content", "size"}` |

`tree?path=<dir>&recursive=true` returns the same metadata fields for all descendants in one response. It reads no file bodies and applies the same path, symlink and `.git` exclusions as a shallow listing. The default listing remains one directory.

The dashboard listing reads candidate frontmatter through the closing YAML delimiter, without decoding document bodies. An absent optional root is empty; discovery/read failures are listed in `errors`. Invalid section names return `400 VIEWER_PATH_INVALID`. The browser parses YAML and reports malformed entries. File paths and symlinks obey the same working-tree guards.

`default_branch` is the branch checked out in the registered work tree (`HEAD` when detached). An empty `path` is the root. A legacy `ref` query parameter is ignored and cannot select another branch. Errors are `{"error": {"code", "message"}}`: `VIEWER_REPO_UNKNOWN`, `VIEWER_PATH_NOT_FOUND` (absent or a symlink), `VIEWER_NOT_FOUND` (no such endpoint or file) with `404`; `VIEWER_PATH_INVALID` (a leading `/`, a `.git` segment, a backslash, an empty, `.` or `..` segment) with `400`.

## 3. Local and read-only

- Bound to `127.0.0.1` only.
- A request whose `Host` header is not `127.0.0.1:<port>` or `localhost:<port>` is `403 VIEWER_HOST_REFUSED`, so a page
  on another site cannot read repository content through the browser by DNS rebinding. No response carries a CORS
  header.
- `GET` only: every other method is `405 VIEWER_METHOD_NOT_ALLOWED`. No endpoint writes, commits or fetches.
- **Approvals stay out**: the viewer records no gate decision, handoff choice or question answer
  (`CAP-DLV-human-interaction`) and has no connection to the integration MCP tools (`CAP-INT-mcp-services`). Every
  approval keeps its existing path.

Any other path serves a file the bundled app lists, looked up by its decoded path (`/` is `index.html`); anything
else is `404`, so no encoded `..` or absolute path reaches a file outside the bundle.

## 4. The page

The page is the viewer moved from autohub, with a repository picker and a label for the checked-out branch. Its tabs read only the registered working tree:

- **Dashboard**: milestones, proposal anchors and feedback load independently (§4.1).
- **문서 읽기**: the Living Spec under `docs/`, grouped by chapter, with in-page links between documents by ID.
- **Proposals** and **Specs**: `docs/proposals/PROP-*/proposal.md` and `specs/<YYYY-MM>/<bundle>/spec.md`, with their
  bundle files, filters and task progress.
- **로드맵**: the milestones under `docs/roadmap/` in the registered working tree (§5).
- **파일 탐색**: the repository working tree, with Markdown, frontmatter and Mermaid rendering.

Documents are parsed in the browser, so the server never runs a repository's own devkit and repositories pinning
different `devkit-spec` versions are all readable. A document with unknown kinds or fields renders like any other; one
whose frontmatter is not valid YAML is listed among the documents that could not be read and the others are still
shown. Rendered Markdown and SVG pass through DOMPurify.

### 4.1 Dashboard loading and tab caches

- **Selective reads**: WHEN a local dashboard section opens, it MUST list frontmatter only for direct `docs/roadmap/MS-*.md` files, `docs/proposals/PROP-*/proposal.md` anchors, or non-README Markdown below any `feedback/` directory within `docs/` or `specs/`. Check: `tests/integration/features/browse/test_worktree.py`.
- **Initial pages**: WHEN a section opens through a source with `dashboardList`, it MUST request full bodies only for its first 6 eligible milestones, 9 proposals or 6 feedback entries. All candidate headers are read once to determine global ordering and exact counts. Check: `frontend/src/lib/features/dashboard/loading.test.ts`.
- **Page ordering**: WHEN Load more is selected, the section MUST append at most one page using the same ordered list. Milestones order by active then planned; proposals by review, draft then accepted; open feedback by critical, blocked, workaround then friction, followed by unknown severities. Each group sorts by ID, then path to resolve ties. Membership and sort metadata stay fixed until Refresh or a fresh tab load after expiry. Check: `frontend/src/lib/features/dashboard/loading.test.ts`.
- **Page failure**: IF a body page fails, THEN the section MUST retain its previous cards and cursor and offer Retry for that page. Check: `frontend/src/lib/features/dashboard/DashboardView.test.ts`.
- **Independent sections**: WHEN a section finishes, the dashboard MUST display its cards without waiting for other sections. Pending and failed sections MUST show loading or error state with an unknown count instead of a successful empty state. Check: `frontend/src/lib/features/dashboard/DashboardView.test.ts`.
- **Cache reuse**: WHEN the same source identity and branch reopen a dashboard section within 30 seconds of successful list completion, the viewer MUST reuse its list and successfully displayed pages, including the expanded card count. Page loads MUST NOT renew the list expiry. Full document indexes and roadmap results remain reusable for 30 seconds after their successful completion. Each source retains at most eight purpose entries. Failed pages MUST NOT replace a successful cached snapshot; aborted scans MUST NOT be cached. Check: `frontend/src/lib/features/dashboard/loading.test.ts`, `frontend/src/lib/features/dashboard/DashboardView.test.ts` and `frontend/src/lib/RoadmapView.test.ts`.
- **Freshness**: WHEN the dashboard Refresh button is selected, the viewer MUST invalidate that source's result caches and reload the sections. Expired entries reload on the next access. Browser reload clears memory; there is no background filesystem subscription. Check: `frontend/src/lib/features/dashboard/DashboardView.test.ts`.
- **Disposal**: WHEN the repository or branch changes or a view is disposed, pending work MUST NOT publish to the replacement view or populate a refreshed cache generation. Check: `frontend/src/lib/features/dashboard/DashboardView.test.ts` and `frontend/src/lib/features/dashboard/loading.test.ts`.

The local source supports recursive metadata requests to avoid one HTTP call per directory. Library hosts without `dashboardList` retain selective full-document discovery to determine ordering and counts; their cold load may read all matching bodies, while the UI still pages cards. Other library hosts use a queue of at most six concurrent requests per scan; a completed request immediately frees its worker for queued work.

## 5. Roadmap

- **Order**: `active`, then `planned`; `done` and `dropped` appear only with the history toggle. Within a status, by
  ID.
- **Readiness**: a milestone is ready when every milestone in its `depends_on` is `done` or `dropped`. A `depends_on`
  naming no milestone is shown as unknown and never counts as satisfied.
- **Source**: milestones and members come from the registered working tree. Other branches are not enumerated.
- **Members**: direct PROP anchors whose `milestone` names the milestone in the registered working tree. Rejected proposals are not members.
  SPEC milestone metadata is ignored, including historical metadata; SPECs never replace proposals by slug.
  The roadmap loader reads milestone and proposal anchors only. Direct proposals do not certify completion.
  One member per slug is displayed.

## 6. The library for autohub

`packages/devkit-viewer/frontend/` is one Svelte 5 source with two outputs:

- the page, built by Vite into `src/devkit_viewer/static/` and committed. It is the tracked generated artifact
  `viewer-assets` in `.devkit/generated.toml` (`CAP-GEN-tracked-artifacts`): `devkit generated check viewer-assets`
  rebuilds it from the lockfile in a clean checkout and fails when the committed build differs. Installing devkit from
  Git therefore needs no Node; only changing the frontend does.
- the component library `devkit-viewer` (`svelte-package`), whose `npm pack` tarball autohub commits under its
  `vendor/` and depends on with `file:`. Its root entry exports `SddViewer`, `KnowledgeViews`, `RoadmapView`,
  `httpDataSource`, `normalizeTree`, `buildRoadmap` and the `RepositoryDataSource` type; `svelte` is a peer
  dependency; the tarball holds no file of the page or the server. Nothing is published to a registry.

A host passes its own `RepositoryDataSource` (`info`, `tree(path, ref)`, `blob(path, ref)`, optional `refs`, `treeRecursive(path, ref)` and `dashboardList(section, ref, signal)`), keeping
authentication and renewal on its side. autohub's Git browser and run and decision panels are not part of the
library.


## Immutable local proposal review page

`GET /review/<registered-repository-id>/<32-hex-generation-id>` reads exactly one `proposal-review` artifact
through the registered repository's configured local shared adapter. This exact-generation route is the exception in
`ADR-viewer`; ordinary working-tree reads remain unchanged. The route accepts no path,
remote URL, adapter selector or revision expression. Remote adapters are unavailable here. It calls only exact
`get`, never list, put or sweep. Namespace, kind, digest and expiry are validated. Source SHA, language and expiry
are prominent; the artifact is evidence for that source, not a claim that the branch is still current.

The page displays escaped Markdown source inside a readable preformatted block: hostile HTML, links and scripts
cannot execute. It uses no-store and a restrictive Content-Security-Policy. Existing loopback, Host, no-CORS and
GET-only controls apply. Missing/remote reports return 404, expired reports 410 and malformed/corrupt reports 400,
with refresh instructions for the Host; the viewer never regenerates. No frontend rebuild or automatic viewer
launch is involved. The backend has a narrow dependency on shared.api, shared.errors and shared.local for this read.
