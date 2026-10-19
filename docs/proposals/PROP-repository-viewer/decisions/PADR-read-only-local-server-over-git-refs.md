---
id: PADR-read-only-local-server-over-git-refs
title: Read-only local server over Git refs
summary: Serves several registered repositories from one foreground local process that reads committed content through Git at any ref, binds to the loopback interface, writes nothing and keeps every approval on its existing path.
proposal: PROP-repository-viewer
status: draft
created_at: 2026-10-19
---

# [PADR-read-only-local-server-over-git-refs] Read-only local server over Git refs

- **Status**: Draft
- **Date**: 2026-10-19

---

## 1. Context & Problem Statement

The viewer reads through a `RepositoryDataSource` (`info`, `tree(path, ref)`, `blob(path, ref)`). devkit's server must
provide it for several local repositories at once, show work that lives on `plan-` and `dev-` branches
(`ADR-milestone-documents`: the base shows only merged state), stay safe as a local web server, and decide whether
the viewer takes part in approvals.

---

## 2. Decision Drivers

- No path outside a registered repository is reachable.
- Any branch is readable without switching a checkout or fetching.
- No new runtime dependency where the standard library suffices.
- No daemon (`ARCH-01-introduction-and-goals` §3.4).
- Each approval keeps one path (`CAP-DLV-human-interaction`, `CAP-INT-mcp-services`).
- Repositories pinning different `devkit-spec` versions are all readable.

---

## 3. Considered Options

### Reads

- **Working tree files**: shows uncommitted edits, but needs path traversal guards and cannot show other branches.
- **Git objects at a ref (Selected)**: `git ls-tree` and `git cat-file` reach only paths in the ref's tree, read any
  local branch, and never touch a checkout.

### Server stack

- **Starlette or a similar framework**: new dependencies for a GET-only local server.
- **Standard library `http.server` (Selected)**: `ThreadingHTTPServer` with GET handlers.

### Registration

- **A user-level configuration file**: a new file format to maintain.
- **Command options (Selected)**: `--repo PATH` (repeatable) and `--scan DIR` (each direct child that is a Git
  repository with `.devkit/config.toml`, for a workspace such as workbench's `repos/`).

### Parsing

- **Run each repository's `devkit spec list --format json`**: needs each repository's own environment.
- **Parse in the browser, as autohub does (Selected)**: the server serves bytes; unknown kinds and fields render as
  plain documents and never fail the view.

### Approvals

- **Record answers from the viewer**: allowed for `record` answers by `CAP-DLV-human-interaction` §1, but the waiting
  agent sees them only at its next `devkit workflow next`, and the server would need write access, a committer and a
  token.
- **Grant integration approval from the viewer**: the `integration_integrate` authority is bound to a request in the
  memory of the stdio MCP process the host started; a separate server cannot grant it without replacing that path.
- **Read-only, approvals out (Selected)**.

---

## 4. Decision Outcome

- **Process**: `devkit viewer serve [--repo PATH]... [--scan DIR] [--port N]` runs in the foreground until
  interrupted. stdout carries one sentinel, `[VIEWER: url=<url> repos=<n>]`; refusals are advisories with stable
  codes (an unknown or duplicate repository ID, no repository registered, port in use); access logs appear only
  under `-v`.
- **Repository ID**: the directory name; two registered repositories with the same name are refused.
- **API**, GET only, the `tree` and `blob` shapes matching autohub's so `httpDataSource` works unchanged:
  `/api/repos`, `/api/repos/{id}/info` (the checked-out branch as `default_branch`), `/api/repos/{id}/refs` (local
  branches), `/api/repos/{id}/tree?path=&ref=`, `/api/repos/{id}/blob?path=&ref=`. `refs` is an optional member of
  `RepositoryDataSource`; without it the roadmap view reads the default branch only.
- **Refs**: resolved with `git rev-parse --verify --end-of-options`; remote-only branches are not read and nothing is
  fetched.
- **Safety**: binds `127.0.0.1` only, refuses a request whose `Host` header is not the loopback address or
  `localhost` at the bound port (DNS rebinding), sends no CORS headers, and has no write endpoint.
- **Roadmap**: milestones by status (`done` and `dropped` behind a history toggle), `depends_on` order and readiness,
  and members (proposals and specs naming the milestone) on the default branch and, through `refs`, on local
  `plan-` and `dev-` branches.
- **Out**: the working tree's uncommitted content, open workflow requests, and every write.

---

## 5. Consequences

- Uncommitted edits are not visible; a person sees their document after committing it. Showing the working tree is a
  possible follow-up.
- Reading every activity branch is bounded by the number of local branches; the roadmap view reads them on demand.
- The viewer never changes what an agent or a person approves, or where.
