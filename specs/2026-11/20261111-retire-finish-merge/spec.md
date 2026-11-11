---
id: SPEC-retire-finish-merge
title: Retire worktree finish --merge
summary: Retires worktree finish --merge so that integration integrate --route local is the one local landing route, dropping the finish guard group and the base push only that path ran.
status: planned
created: 2026-11-11
related_capabilities:
  - CAP-WT-task-worktrees
  - CAP-INT-mcp-services
  - CAP-DLV-workflow-envelopes
  - CAP-DLV-delivery-workflows
related_usecases:
  - UC-drive-development-to-integration
  - UC-handle-delivery-problems-and-exceptions
workflow: sdd-spec-feature
---

# [SPEC-retire-finish-merge] Retire worktree finish --merge

## 1. Problem Statement & Motivation

devkit has two implementations that land a task branch on the local base: `devkit worktree finish --merge`
(`finish(merge=True)` in the worktree feature) and `devkit integration integrate --route local` (the integration
service, `CAP-INT-mcp-services`). They have diverged. `finish --merge` runs the `devkit.finish_guard` extensions,
fetches the base upstream, pushes the base after landing and refuses a moved target. The integration route builds a
merge onto a moved target, settles generated-file conflicts, binds an approval digest and runs no content guard,
fetch or push. Agents and documents choose between them inconsistently, and every Git safeguard has to be kept twice.

The review-refactor code pass (finding AO-01) recorded the user's decision: retire `finish --merge` so that
`devkit integration integrate --route local` is the one local landing route. `worktree finish` without `--merge`
(cleanup after a confirmed merge, PR-route cleanup, `--discard`, `--local-only`) stays.

### What `finish --merge` alone did, and where it goes

| Behavior of `finish --merge` | Outcome | Reason |
| --- | --- | --- |
| `devkit.finish_guard` extensions (the workflow envelope hold) before landing | Dropped from tooling; the group is retired | `CAP-INT-mcp-services` §4 (`ADR-post-merge-verification`) forbids content finish guards in integration. The hold stays where the accepted contract puts it: `devkit workflow next` holds the `dev-integration` gate while a unit is blocked, and `spec-integrate` step 4 runs `devkit workflow envelope check` with the source runtime before approval |
| Fetch of the base upstream and `WORKTREE_BASE_BEHIND` | Dropped | It only protected the push below |
| Push of the base to its upstream (`push=`, `WORKTREE_PUSH_REJECTED`, `WORKTREE_PUSH_FAILED`) | Dropped | `ARCH-04-2-delivery-policy`: the local route MUST exclude fetch and push. Publishing the base is a separate Git effect under the Host's publication authority |
| `WORKTREE_MERGE_NOT_FF` for a target that moved | Replaced | The integration route builds and checks the merge onto a moved target (`ADR-local-and-pull-request-integration`) |
| PR policy, detached or dirty base, recorded-base mismatch, branch moved during the check, integration lock, committer identity, deletable branch | Kept | `plan_finish`, `validate_finish` and the integration service already enforce each |

## 2. User Stories

- **US-1**: As an agent integrating a verified branch locally, I want exactly one landing command, so that every local
  landing gets the same moved-target, generated-file, approval and cleanup handling.
- **US-2**: As an agent following older guidance, I want `finish --merge` to refuse with a stable code that names the
  integration commands, so that I switch routes without guessing.
- **US-3**: As a maintainer, I want the dropped behaviors and their reasons recorded in a decision and the Living
  Spec, so that nobody reintroduces a second landing path or expects a push that no longer happens.

## 3. Non-Goals

1. **Scope Excluded**: adding a push, fetch or workflow-envelope check to `devkit integration integrate`; its content
   boundary (`CAP-INT-mcp-services` §4) and no-network local route stay as they are.
2. **Scope Excluded**: changing `finish` without `--merge`, `--discard`, `discard()`, the post-finish extension group
   or the `before_remove` callback (another unit changes `before_remove`).
3. **Scope Excluded**: retiring `--local-only`. It stays accepted on `finish` for the guidance that names it.
   - **When to Reconsider**: a later cleanup of no-op flags; `finish` now makes no network call with or without it.
4. **Scope Excluded**: rewriting accepted ADRs or completed specs; history keeps its `finish --merge` wording and the
   new ADR supersedes the affected clauses.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] `finish --merge` refuses with the integration route
- **Given** a repository with a clean task worktree on `dev-demo` whose branch the base does not contain
- **When** the agent runs `devkit worktree finish dev-demo --merge` from the base
- **Then** the command exits `2` with `(WORKTREE_MERGE_RETIRED)` at level `ERROR`, category `INPUT_ERROR`, and one
  `[FIX]` line naming `uv run devkit integration prepare dev-demo --route local` and
  `uv run devkit integration integrate dev-demo --route local --expected-digest <digest>`
- **And** the base HEAD, the branch, its worktree and its marker are unchanged, and no post-finish extension runs
- **And** `devkit worktree finish --help` does not list `--merge`

### [AC-02] The library `finish` keeps only cleanup
- **Given** the `devkit_agt.features.worktree` public API
- **When** a caller passes `merge`, `pull_request`, `guard`, `network` or `merge_method` to `finish`
- **Then** Python raises `TypeError`, and `FinishResult` has no `push` field
- **And** `finish` on a branch the base already contains removes the worktree, deletes the branch under
  `delete_branch`, prints `[WORKTREE_FINISHED: <branch> path=<path> merged=no removed=yes branch_deleted=yes
  discarded=no]` and exits `0`; on an unmerged branch it still refuses with `WORKTREE_UNMERGED`, whose `[FIX]` names
  `uv run devkit integration prepare <branch> --route local` and no longer names `finish --merge`

### [AC-03] Cleanup commands stay local and unchanged
- **Given** a branch already merged into the base (local integration landed, or its pull request merged)
- **When** the agent runs `devkit worktree finish <branch>` or `devkit worktree finish <branch> --local-only`
- **Then** both exit `0` with the cleanup of AC-02 and no `git fetch`, `git push` or `git ls-remote` call
- **And** `devkit worktree finish <branch> --discard` keeps its current behavior and output

### [AC-04] Local integration covers every branch `finish --merge` landed
- **Given** a task worktree branch, a `start --no-worktree` branch whose base checkout was switched back, or a
  `plan-<slug>` branch, each containing the base HEAD or not
- **When** the agent runs `devkit integration integrate <branch> --route local` under `dev-integration = "auto"`
- **Then** the base lands the branch, the worktree (when there is one) is removed, the branch is deleted, and the
  run makes no `git fetch` or `git push` call

### [AC-05] The finish guard group is retired and the hold stays
- **Given** an installed devkit-agt
- **When** a caller lists `importlib.metadata.entry_points(group="devkit.finish_guard")`
- **Then** devkit-agt registers none, and `run_finish_guards`, `FINISH_GUARD_GROUP`, `BlockedError`,
  `GuardFailedError`, `BaseBehindError`, `PushFailedWarning`, `PushRejectedWarning` and the workflow feature's
  `finish_guard` are no longer importable; the codes `WORKTREE_BLOCKED`, `WORKTREE_GUARD_FAILED`,
  `WORKTREE_BASE_BEHIND`, `WORKTREE_PUSH_FAILED` and `WORKTREE_PUSH_REJECTED` no longer exist
- **And** for a unit holding an unresolved problem, `devkit workflow envelope check --unit <dir> --format json`
  still reports `"blocked": true` with one `problems` entry per problem, and `devkit workflow next --unit <dir>`
  passes no gate from the problem's stage on

### [AC-06] Guidance and the Living Spec name one landing route
- **Given** the selected bundles' sources, `docs/` outside history (`docs/decisions/`, `docs/materials/`) and the
  package sources
- **When** `rg -n "finish[^|]*--merge" packages docs guides` runs, excluding history and tests
- **Then** every match states the retirement (`WORKTREE_MERGE_RETIRED`) or names the integration commands; the spec
  bundle's branch-only integration step (`references/branches.md` §2) and the Backlog decomposition return
  (`references/backlog.md`) name `devkit integration prepare` and `devkit integration integrate --route local`
- **And** `devkit sync --check` exits `0` after the sync outputs are committed

### [AC-07] The decision is recorded
- **Given** the accepted ADR clauses that require or describe `finish --merge` (`ADR-local-and-pull-request-integration`,
  `ADR-orchestration-workers`, `ADR-worktrees-and-scope`) and the `devkit.finish_guard` entry point clause
  (`ADR-package-ownership-and-release-version`)
- **When** `devkit rules check` runs
- **Then** a new accepted ADR supersedes exactly those clauses, states the dropped behaviors of §1 with their reasons,
  and reports no violation

## 5. Assumptions

1. The envelope hold is not carried into the integration route: `CAP-INT-mcp-services` §4 and
   `ADR-post-merge-verification` forbid it, and the workflow gate plus `spec-integrate` step 4 keep the hold. The
   rejected alternative, a hold check inside `IntegrationService`, would need a decision reversing that ADR.
2. With its only caller gone, the `devkit.finish_guard` group is retired rather than kept dormant: a public extension
   group nothing calls would document a refusal that never happens.
3. Push is not carried: `ARCH-04-2-delivery-policy` requires the local route to exclude fetch and push.
4. The Backlog decomposition return lands through `devkit integration integrate plan-<slug> --route local` on the
   authority Backlog step 1 establishes; under `dev-integration = "ask"` the Host passes the prepared digest.
5. `--merge` stays a hidden option so the refusal carries a stable code and `[FIX]`; no other compatibility path exists
   (no external consumers).
6. This changes MUST clauses of `CAP-WT-task-worktrees` and `CAP-DLV-workflow-envelopes` and accepted ADR clauses, so
   the new ADR (AC-07) is required before implementation.
