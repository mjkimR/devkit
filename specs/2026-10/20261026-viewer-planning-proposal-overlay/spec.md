---
id: SPEC-viewer-planning-proposal-overlay
title: Viewer overlay of Planning proposals
summary: The viewer shows each PROP-<slug> from its plan-<slug> worktree, local branch or remote-tracking ref over the checkout's proposal cards, loaded after the checkout without fetching.
status: completed
created: 2026-10-26
related_capabilities: [CAP-VIEW-repository-viewer]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-viewer-planning-proposal-overlay] Viewer overlay of Planning proposals

## 1. Problem Statement & Motivation

`devkit viewer serve` reads only the registered checkout's working tree (`ADR-viewer-working-tree`,
`CAP-VIEW-repository-viewer`). A proposal under Planning lives on its `plan-<slug>` branch, usually in a sibling
worktree, so the Dashboard proposal section and the Proposals tab show the stale copy from the main checkout. The
earlier branch reads were slow because every read went through `gh`; reading only `docs/proposals/PROP-<slug>/` from
local worktrees and refs is cheap.

## 2. User Stories

- **US-1**: As a developer, I want each proposal's Dashboard card and Proposals entry to show its Planning version and
  the source it came from, so that I review the current proposal without switching checkouts.
- **US-2**: As a developer, I want the checkout's cards to appear as fast as today, so that a slow or failed Planning
  scan never delays or breaks the page.

## 3. Non-Goals

1. **Scope Excluded**: roadmap membership and milestone computation, which stay on the checkout.
2. **Scope Excluded**: pull requests, `gh`, fetching and any write to the repository.
3. **Scope Excluded**: an overlay for specs, feedback, milestones, Living Spec documents or the Files tab.
4. **Scope Excluded**: a branch picker and filesystem watchers.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Planning sources and precedence
- **Given** a repository whose checkout is on `main`, with `plan-a` checked out in a linked worktree, local branches
  `plan-a` and `plan-b`, and remote-tracking refs `origin/plan-a`, `origin/plan-b` and `origin/plan-c`
- **When** `GET /api/repos/<id>/planning-proposals` is requested
- **Then** it answers `200` with exactly one source per slug: `worktree:plan-a` (label `worktree plan-a`),
  `branch:plan-b` (label `plan-b`) and `remote:origin/plan-c` (label `origin/plan-c`), and the PROP-a item carries
  the worktree's saved uncommitted content of `docs/proposals/PROP-a/proposal.md`.

### [AC-02] One proposal per Planning branch
- **Given** a `plan-a` source that also contains `docs/proposals/PROP-other/proposal.md`, a `plan-new` source whose
  PROP-new does not exist in the checkout, and a `plan-empty` source without `docs/proposals/PROP-empty/proposal.md`
- **When** the Planning proposals are listed
- **Then** the items are exactly `docs/proposals/PROP-a/proposal.md` and `docs/proposals/PROP-new/proposal.md`; the
  PROP-other copy and the `plan-empty` source contribute no item.

### [AC-03] Batched, read-only Git use
- **Given** any number of Planning branches
- **When** one Planning scan runs
- **Then** it starts at most one `git worktree list`, one `git for-each-ref` and one `git cat-file --batch` process,
  starts no `fetch` and no `gh`, and leaves the repository's refs and `git status --porcelain` output unchanged.

### [AC-04] Source-scoped reads
- **Given** the source `worktree:plan-a` with an untracked `docs/proposals/PROP-a/materials/notes.md` and the source
  `branch:plan-b`
- **When** `tree?path=docs/proposals/PROP-a&recursive=true&source=worktree:plan-a` and
  `blob?path=docs/proposals/PROP-b/proposal.md&source=branch:plan-b` are requested
- **Then** both answer `200` with that source's listing and saved or committed content, in the payload shapes of the
  checkout reads.

### [AC-05] Source refusals
- **Given** the sources of AC-01
- **When** `tree` or `blob` names a source with a path outside that source's `docs/proposals/PROP-<slug>/`, an unknown
  or non-winning source (`branch:plan-a`), or a revision expression (`HEAD`, `branch:plan-b^`)
- **Then** the path case answers `400` `VIEWER_SOURCE_PATH_REFUSED`, the source cases answer `404`
  `VIEWER_SOURCE_UNKNOWN`, a symlink, `.git` or otherwise invalid path keeps the checkout's errors, and `source` on
  `info`, `dashboard-list` and `planning-proposals` is ignored.

### [AC-06] Checkout cards first, overlay in place
- **Given** a Dashboard whose checkout proposal cards have rendered and a source that supports the Planning overlay
- **When** the separate Planning request completes
- **Then** the matching cards keep their positions and show the Planning title, status, summary and a source badge;
  Planning-only active proposals are appended after the last checkout card once no checkout page remains; and the
  active count includes them.

### [AC-07] Slow or failed overlay
- **Given** a Planning request that is pending or fails
- **When** the checkout proposal list completes
- **Then** the checkout cards and count are displayed as without the overlay, and a failure shows a non-alert note
  instead of an error state for the section.

### [AC-08] Ordering, caching and Refresh
- **Given** a Planning overlay that has been applied for a source and branch
- **When** the proposal list is rebuilt by Refresh or after its 30-second expiry
- **Then** its order and membership use the checkout headers merged with that overlay, and a fresh Planning request
  again updates the cards in place; Refresh discards the cached Planning result, a cached result is reused within 30
  seconds, and aborted or superseded Planning work neither publishes nor populates a refreshed cache generation.

### [AC-09] Proposals tab reads the same source
- **Given** an overlaid PROP-a from `worktree:plan-a`
- **When** the Proposals tab lists proposals, or the Dashboard card for PROP-a is selected
- **Then** the entry shows the Planning metadata and source badge, the Proposals tab opens it, and its bundle files are
  read with `source=worktree:plan-a`; no "View raw" button opens the checkout copy of a Planning document.

### [AC-10] Hosts without the overlay
- **Given** a `RepositoryDataSource` without `planningProposals`
- **When** the Dashboard, Proposals tab and roadmap load
- **Then** they render and request as before, and the roadmap never requests the Planning overlay.

## 5. Security

The `source` parameter selects only a source from the server's enumeration for that request; no revision expression,
ref name or unvalidated path reaches Git. A worktree source is read with the checkout's path, symlink and `.git`
guards, and only below its `docs/proposals/PROP-<slug>/`. The server stays loopback-only and `GET`-only and writes
nothing.

## 6. Assumptions

- A source exists for the branch `plan-<slug>` only when `<slug>` matches `[A-Za-z0-9][A-Za-z0-9._-]*` without `..`;
  `plan-a/b` and remote names containing `/` are ignored.
- A worktree source is any worktree other than the registered checkout whose branch is `refs/heads/plan-*` and whose
  directory exists; detached, bare and missing worktrees are skipped.
- When the registered checkout itself is on `plan-<slug>`, that slug has no Planning source: the checkout already shows
  it.
- Of several remote-tracking refs for one slug, the one whose remote name sorts first wins.
- A local branch or remote-tracking ref already merged into the checkout's `HEAD` is not a source: it holds nothing the
  checkout lacks. A worktree stays a source, because it can hold saved, uncommitted edits.
- A branch source's content is its commit as enumerated for the request. A detail `tree` or `blob` request enumerates
  the sources again (`git worktree list`, `git for-each-ref`) and then reads with one more Git process for a branch
  source or from the files of a worktree; only the Planning scan is batched.
- The Dashboard keeps the last applied overlay per source and branch in memory as the seed of the next list build.
  Once the fresh scan of that build answers, a seeded card whose source it no longer reports shows the checkout's
  header again, and a seeded Planning-only card leaves the list, without reordering the others.
