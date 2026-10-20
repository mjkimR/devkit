---
id: PADR-github-pull-request-adapter-in-devkit-worktree
title: GitHub pull request adapter in devkit.worktree
summary: Remote and pull request operations run through gh behind a narrow injectable protocol in devkit.worktree, GitHub only; other remotes, a missing or unauthenticated gh, merge queues, auto-merge and admin bypass are refused before the confirmation.
proposal: PROP-integration-pull-request-cleanup
status: draft
created_at: 2026-10-20
---

# [PADR-github-pull-request-adapter-in-devkit-worktree] GitHub pull request adapter in devkit.worktree

- **Status**: Draft
- **Date**: 2026-10-20

---

## 1. Context & Problem Statement

The integration service and `devkit worktree finish` perform no remote write today; `gh` is used only read-only by the
stale-branch report (`worktree/stale.py`, an injectable `GhRunner` with a 60-second bound). The pull request route
needs remote identity, merge-method permissions, PR lookup, creation and state, a merge with the head pinned and a
conditional remote branch deletion. `integration` may import `worktree`, never the reverse, and `worktree` uses only
`core` and `advisory`.

## 2. Decision Drivers

- One platform is in use (GitHub); no second one is requested.
- Tests run without network through an injectable runner, as the stale report does.
- What cannot be verified locally is refused before the confirmation, never discovered after it.

## 3. Considered Options

- A provider entry-point group (`devkit.pull_request_provider`) with a GitHub implementation.
- GitHub only, through `gh`, behind a narrow protocol in `devkit.worktree` beside `run_gh`.
- Direct REST calls with a token devkit reads itself.

## 4. Decision Outcome

The second option. `devkit.worktree` gains a pull request port (remote and repository identity, merge-method
permissions and applicable rules, PR find/create/update by head and base, PR state with `headRefOid`, `baseRefOid`,
`mergeCommit` and `state`, merge with `--merge --match-head-commit <source>` and a devkit-composed subject, and remote
branch deletion leased on the expected SHA) implemented with `gh`, with no terminal prompt and a bound per call.
`gh pr merge --delete-branch` is not used (it deletes the local branch outside devkit's guards). Refused before the
confirmation with stable codes: a remote whose URL is not GitHub, `gh` missing or not authenticated, a cross-repository
(fork) PR, a merge queue on the target, and any path that would need `--auto` or `--admin`. Authentication is `gh`'s;
devkit stores no token.

## 5. Consequences

- A second platform later becomes an entry-point group over the same port; no consumer exists yet.
- GitHub-specific behaviour (merge commit identity and signature, rules readable only by admins) is disclosed, not
  hidden.
- `devkit worktree finish` itself stays local-merge only; the port is used by the integration service's pull request
  route and by its cleanup.
