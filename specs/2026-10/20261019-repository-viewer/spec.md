---
id: SPEC-repository-viewer
title: Local multi-repository SDD viewer owned by devkit
summary: "Moves the autohub SDD repository viewer into devkit as its source owner, adds a roadmap view for milestone documents, and packages it with a local server that serves several repositories at once; the viewer stays read-only and grants no approvals."
status: completed
created: 2026-10-19
related_capabilities:
  - CAP-DOCS-document-model
  - CAP-GEN-tracked-artifacts
  - CAP-HARN-command-mount
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-repository-viewer] Local multi-repository SDD viewer owned by devkit

## 1. Problem Statement & Motivation

Proposals, specs, the Living Spec and milestones (`ADR-roadmap-in-repository`, `ADR-milestone-documents`) are
repository files. An agent reads them through `devkit spec list`, `resolve` and `refs`; a person has no screen for
them outside autohub, which needs a GitHub-connected project, reads only one repository per view and shows only what
is on one ref. `ADR-roadmap-in-repository` names the cost: "no human-facing roadmap screen until a viewer renders it".

autohub holds a native Svelte viewer for SDD repositories (`SddViewer`, `KnowledgeViews`, `documents.ts`,
`repository.ts`, about 2.5k lines) that reads through a `RepositoryDataSource` (`info`, `tree(path, ref)`,
`blob(path, ref)`). It shows a document's `milestone` as a badge but has no roadmap.

This spec moves that viewer into devkit, which owns its source from now on, adds a roadmap view, and ships it in a new
`devkit-viewer` distribution whose `devkit viewer serve` command serves several local repositories from one process.
The decisions are `ADR-viewer-distribution-and-frontend-build` (distribution, committed build, autohub's vendored
tarball) and `ADR-read-only-local-server-over-git-refs` (Git reads, registration, safety, approvals out).

## 2. User Stories

- **US-1**: As a person working in several devkit repositories, I want one local page that shows each repository's
  Living Spec, proposals, specs and roadmap, so that I can read the plan without autohub or network access.
- **US-2**: As a person deciding the next milestone step, I want to see each milestone's status, its `depends_on`
  readiness and its members, including Units still on `plan-` and `dev-` branches, so that I can judge activation and
  close candidates from one view.
- **US-3**: As the autohub maintainer, I want the same viewer as a Svelte component library I can vendor as a tarball,
  so that autohub stops carrying its own copy.

## 3. Non-Goals

1. **Scope Excluded**: recording approvals, gate decisions, handoff choices or question answers from the viewer, and
   any connection to the integration MCP tools.
   - **Rationale**: `ADR-read-only-local-server-over-git-refs` §3 (Approvals).
2. **Scope Excluded**: any write: editing documents, starting Planning or Development, committing, fetching.
3. **Scope Excluded**: showing open workflow requests (`[REQUEST: ...]`).
   - **When to Reconsider**: people ask for the gate queue on the page; it needs each repository's own devkit to run.
4. **Scope Excluded**: showing uncommitted working tree content.
   - **When to Reconsider**: previewing a document before committing it becomes a recurring need.
5. **Scope Excluded**: remote-only branches, remote hosting, authentication for several users, and GitHub API access.
6. **Scope Excluded**: the autohub change that replaces its copy with the vendored tarball (autohub's own work), and
   autohub's Git browser and run/decision panels (`RepositoryView`, `FileTreeTable`, `FileBlobViewer`,
   `SddExecution`, `SddProposals`, `SddRunLinks`), which stay in autohub.
7. **Scope Excluded**: publishing to the npm registry or PyPI.

## 4. Acceptance Criteria & Behavioral Contracts

The server's error responses are one JSON object `{"error": {"code": "<CODE>", "message": "<text>"}}`. Exit codes
follow `ARCH-08-1-agent-output`: `0` after a normal stop, `2` when the command cannot run.

### [AC-01] Serve registered repositories
- **Given** two Git repositories `alpha` and `beta`
- **When** `devkit viewer serve --repo <alpha> --repo <beta> --port 0` starts
- **Then** the first stdout line is `[VIEWER: url=http://127.0.0.1:<port>/ repos=2]` with the bound port, nothing else is
  written to stdout while it runs, and `GET /api/repos` returns `{"repos": [{"id": "alpha", "default_branch": ...},
  {"id": "beta", ...}]}` sorted by `id`, where `default_branch` is the branch checked out in that repository

### [AC-02] Default and scanned registration
- **Given** a directory holding a Git repository `one` with `.devkit/config.toml`, a Git repository `two` without it,
  and a plain directory `three`
- **When** `devkit viewer serve --scan <dir> --port 0` starts, and separately `devkit viewer serve --port 0` starts with
  no `--repo` or `--scan` from inside the devkit project `one`
- **Then** both register exactly `one`

### [AC-03] Registration refusals
- **Given** two repositories whose directories are both named `same`; a path that is not the top level of a Git work
  tree; a `--scan` directory with no eligible child; no option outside any devkit project; a port already bound
- **When** `devkit viewer serve` starts with each
- **Then** it exits `2` without serving and prints on stderr the advisory `VIEWER_REPO_DUPLICATE`, `VIEWER_REPO_INVALID`,
  `VIEWER_NO_REPOSITORY`, `VIEWER_NO_REPOSITORY` and `VIEWER_PORT_IN_USE` respectively

### [AC-04] Tree at a ref
- **Given** a registered repository whose branch `main` holds `docs/a.md` and `docs/sub/b.md`
- **When** `GET /api/repos/<id>/tree?path=docs&ref=main` and `GET /api/repos/<id>/tree?path=&ref=main`
- **Then** the first returns status `200` and `{"items": [...]}` with exactly `docs/sub` (`type: "tree"`) and `docs/a.md`
  (`type: "blob"`, its `size` in bytes), each with `name` and repository-relative `path`; the second lists the root
  entries

### [AC-05] Blob at a ref, any local branch
- **Given** `docs/a.md` differs between the checked-out `main` and a local branch `plan-x` that is not checked out
- **When** `GET /api/repos/<id>/blob?path=docs/a.md&ref=plan-x`
- **Then** status `200` and `{"path": "docs/a.md", "encoding": "base64", "content": <base64 of the plan-x bytes>,
  "size": <bytes>}`, and the working tree and `HEAD` of the repository are unchanged

### [AC-06] Local branches
- **Given** a registered repository with local branches `main`, `plan-x` and `dev-y` and a remote-tracking branch
  `origin/z`
- **When** `GET /api/repos/<id>/refs`
- **Then** status `200` and `{"default_branch": "main", "branches": ["dev-y", "main", "plan-x"]}`

### [AC-07] Read errors
- **Given** a registered repository
- **When** a request names an unknown repository ID, an unknown ref, a ref starting with `-`, a path absent at the ref,
  a path containing a `..` or `.` segment, or a `blob` path that is a directory
- **Then** the status and code are `404 VIEWER_REPO_UNKNOWN`, `404 VIEWER_REF_UNKNOWN`, `404 VIEWER_REF_UNKNOWN`,
  `404 VIEWER_PATH_NOT_FOUND`, `400 VIEWER_PATH_INVALID` and `404 VIEWER_PATH_NOT_FOUND` respectively

### [AC-08] Local-only and read-only
- **Given** a running server
- **When** it is inspected and sent requests
- **Then** it is bound to `127.0.0.1` only; a request whose `Host` header is not `127.0.0.1:<port>` or
  `localhost:<port>` gets `403 VIEWER_HOST_REFUSED`; `POST`, `PUT`, `PATCH` and `DELETE` on any path get `405`; and no
  response carries an `Access-Control-Allow-Origin` header

### [AC-09] Bundled page
- **Given** a running server from an installed `devkit-viewer` wheel
- **When** `GET /` and `GET` of an asset path the page references
- **Then** both return `200`, `/` with `text/html` content, the asset with a JavaScript or CSS content type; a path
  outside the bundled files and outside `/api/` returns `404`

### [AC-10] Repository and branch switch in the page
- **Given** the page served for two repositories
- **When** a person picks the second repository, then a branch from its `refs`
- **Then** every viewer read goes to `/api/repos/<second id>/...` with that branch as `ref`

### [AC-11] Roadmap by status and readiness
- **Given** milestones MS-a (`done`), MS-b (`active`, `depends_on: MS-a`), MS-c (`planned`,
  `depends_on: MS-b`) and MS-d (`dropped`) under `docs/roadmap/`
- **When** the roadmap view is computed with history hidden, then shown
- **Then** hidden history lists MS-b then MS-c, MS-b ready and MS-c not ready (waiting for MS-b); shown history
  also lists MS-a and MS-d; a `depends_on` naming no milestone is reported as unknown, never as satisfied

### [AC-12] Roadmap members across branches
- **Given** on the default branch a proposal PROP-p (milestone MS-b, draft), a rejected proposal PROP-r
  (milestone MS-b), a completed spec SPEC-s (milestone MS-b), an accepted proposal PROP-h
  (milestone MS-b); and on local branch `dev-h` the spec SPEC-h (milestone MS-b, in-progress) that replaced it
- **When** MS-b's members are computed from the default branch and the local `plan-` and `dev-` branches
- **Then** the members are PROP-p (unsettled), SPEC-s (settled) and SPEC-h (unsettled, branch `dev-h`); PROP-r
  and PROP-h are not listed

### [AC-13] Unknown kinds and broken documents
- **Given** a repository with a document whose frontmatter has fields and kinds the viewer does not know, and another
  whose frontmatter is not valid YAML
- **When** the documents are indexed
- **Then** the first is indexed and renders like any document; the second is listed among the documents that could not
  be read, and every other document is indexed

### [AC-14] Library tarball for autohub
- **Given** the frontend project
- **When** its library is packaged and `npm pack` runs on it
- **Then** the tarball's `package.json` exports `SddViewer`, `httpDataSource` and the `RepositoryDataSource` type from
  its root entry, declares `svelte` as a peer dependency, and contains no file of devkit's app or server

### [AC-15] Committed build is current and reproducible
- **Given** the committed app build under `src/devkit_viewer/static/` and its artifact entry in `.devkit/generated.toml`
- **When** `devkit generated check` runs on an unchanged checkout, and again after the app is rebuilt from the same
  lockfile
- **Then** both runs exit `0` and the rebuild changes no tracked file; after a frontend source changes without a
  rebuild, `devkit generated check` exits non-zero naming the artifact

### [AC-16] Mounted command
- **Given** `devkit-viewer` installed beside `devkit-agt`
- **When** `devkit viewer --version` and `devkit viewer serve --help`
- **Then** the first prints `[VERSION: devkit-viewer <version>]`; the second exits `0`; without `devkit-viewer`
  installed, `devkit` itself keeps working

## 5. Security, Privacy & Compliance Considerations

- The server only reads Git objects of registered repositories at local refs: no path outside a ref's tree is
  reachable, and nothing is fetched or written (AC-05, AC-07, AC-08).
- Loopback binding, the `Host` check and the absence of CORS headers keep other sites from reading repository content
  through a person's browser, including by DNS rebinding (AC-08).
- Rendered Markdown and Mermaid SVG pass through DOMPurify as in autohub.

## 6. Assumptions

- The page keeps autohub's Korean UI labels; the roadmap view uses Korean labels in the same style.
- `blob` always answers `base64`, which the viewer already decodes, so binary files never break a response.
- When a branch holds SPEC-<slug> and another view holds PROP-<slug>, the spec is the member: the handoff replaced the
  proposal (AC-12).
- The frontend targets Node 22 or later; autohub's own engine range is its concern.
