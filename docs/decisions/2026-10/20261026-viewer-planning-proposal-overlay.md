---
id: ADR-viewer-planning-proposal-overlay
title: Overlay Planning proposals from local plan branches
summary: "For proposals under Planning, we overlay each PROP-<slug> from its plan-<slug> worktree, local branch or remote-tracking ref after the checkout loads, to show current proposals without switching checkouts, accepting one batched local Git scan per load and stale remote copies until a fetch."
status: accepted
created_at: 2026-10-26
---

# [ADR-viewer-planning-proposal-overlay] Overlay Planning proposals from local plan branches

- **Status**: Accepted; replaces part of `ADR-viewer-working-tree`
- **Date**: 2026-10-26
- **Deciders**: @minjae
- **Involved Components/Capabilities**: `packages/devkit-viewer/`, `CAP-VIEW-repository-viewer`

---

## 1. Context & Problem Statement

`ADR-viewer-working-tree` makes every viewer tab read the registered checkout only. A proposal under Planning is edited
on its `plan-<slug>` branch, usually in a sibling worktree, so the Dashboard and Proposals tab show the copy the main
checkout last merged, which can be days behind. The earlier branch reads were slow because every read went through
`gh`; the viewer then dropped branch reads altogether.

Only `docs/proposals/PROP-<slug>/` of each Planning branch is current: the rest of that branch is a stale copy of its
base. The viewer must remain local, read-only, loopback-only and `GET`-only, and its checkout view must not wait for
anything new.

## 2. Decision Drivers

- Show the Planning version of each proposal, including saved uncommitted and untracked files in its worktree.
- Keep the checkout's cards as fast as today; a slow or failed Planning read must not block or break them.
- Read only what is current: one proposal directory per Planning branch.
- No network, `gh`, fetch or write; no arbitrary revision reaches Git.
- Bounded Git cost per page load, independent of the number of files.

## 3. Considered Options

### Overlay proposals from local Planning sources after the checkout (Selected)

- **Overview**: A separate request enumerates `plan-*` worktrees, local branches and remote-tracking refs, reads only
  `docs/proposals/PROP-<slug>/proposal.md` of each, and the page updates matching cards in place.
- **Pros**: Current proposals without switching checkouts; checkout view unchanged; one batched Git read per scan;
  uncommitted Planning files are visible through the worktree.
- **Cons**: A remote-tracking copy is only as current as the last fetch; a second source of content needs a badge so
  the reader knows where it came from.

### Read proposals through `gh` or the pull request

- **Overview**: Ask the forge for each Planning branch's files.
- **Pros**: Always current with the remote.
- **Cons**: Network latency per file, authentication, and the slowness that removed branch reads before.

### Keep the checkout only

- **Overview**: Leave `ADR-viewer-working-tree` unchanged.
- **Pros**: No new code or Git use.
- **Cons**: Proposals under Planning stay stale, which is the problem.

## 4. Decision Outcome

We overlay Planning proposals from local sources. This replaces, for proposals only, the statement of
`ADR-viewer-working-tree` §4 that the UI reads only the current checkout; every other statement of that ADR, the
roadmap included, stays.

- **Sources**: a worktree on `plan-<slug>` (read from its files), else the local branch `plan-<slug>`, else a
  remote-tracking `<remote>/plan-<slug>` as of the last fetch. A ref already merged into the checkout is no source.
  Each source contributes only `docs/proposals/PROP-<slug>/`.
- **Loading**: the checkout's proposal list renders first; one independent request enumerates the sources with one
  `git worktree list` and one `git for-each-ref` and reads every branch source through one `git cat-file --batch`.
  Cards update in place, without reordering, until the next list build.
- **Identity and reads**: each overlaid entry names its source; its bundle files are read with that source, accepted
  only for paths under its own `docs/proposals/PROP-<slug>/` and only as one of the sources enumerated for the
  request. Every other read keeps ignoring source and ref selection.
- **Boundaries**: no fetch, `gh`, pull request or write; worktree reads use the checkout's path, symlink and `.git`
  guards.

The selected option meets every driver; the remote staleness is visible through the badge.

## 5. Consequences

- **Positive**: The Dashboard and Proposals tab show the proposal being planned, with its materials, without a branch
  switch. The checkout view is unchanged when no Planning source exists or the scan fails.
- **Negative / Risks**: Each Planning scan starts up to three Git processes, and each source-scoped `tree` or `blob`
  read of an overlaid bundle up to three more. A remote-tracking source can be stale. Two views of one proposal exist,
  separated only by the badge.
- **Follow-ups**: Extend the overlay to specs under Development only if dev worktrees show the same staleness.

## 6. Confirmation

- `packages/devkit-viewer/tests/integration/features/browse/test_planning.py` proves precedence, per-branch scope,
  the batched read-only Git use and source refusals on real repositories.
- `packages/devkit-viewer/frontend/src/lib/features/dashboard/DashboardView.test.ts` and
  `packages/devkit-viewer/frontend/src/lib/features/knowledge/KnowledgeViews.test.ts` prove the checkout-first,
  in-place overlay and same-source bundle reads.
