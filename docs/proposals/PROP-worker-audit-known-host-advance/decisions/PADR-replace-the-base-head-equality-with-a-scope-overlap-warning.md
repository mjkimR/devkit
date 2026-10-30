---
id: PADR-replace-the-base-head-equality-with-a-scope-overlap-warning
title: Replace the base HEAD equality with a scope-overlap warning
summary: For worker validation, we replace base-checkout HEAD equality with a warning naming base commits after the audit base and base dirty paths inside the write scope, to keep detecting worker escapes without serializing other advances, accepting that out-of-scope escapes go unnamed.
proposal: PROP-worker-audit-known-host-advance
status: draft
created_at: 2026-10-30
---

# [PADR-replace-the-base-head-equality-with-a-scope-overlap-warning] Replace the base HEAD equality with a scope-overlap warning

- **Status**: Draft
- **Date**: 2026-10-30

---

## 1. Context & Problem Statement

A worker's default cwd may be the base checkout (`ADR-orchestration-workers`, Codex native worker execution), so a
relative-path write or a commit can escape its worktree, outside the audited range `<accepted>..<returned>`. The Host
detects that by recording the base checkout's status and HEAD before spawning and requiring both unchanged at
validation (`ADR-orchestration-workers`, committed results and their validation). The same equality stops on every
Host integration and every commit another session makes to the base branch, so the Host serialized independent
integrations behind a running worker (`MAT-git-operator-consumer-pilot`). The pre-spawn HEAD lives only in the Host's
conversation, and `devkit spec worker inspect` reports the base checkout as information only
(`ADR-orchestration-workers`, informational range inspection).

Existing checks already catch part of an escape: a dirty base checkout refuses integration (`WORKTREE_BASE_DIRTY`), and
a worker whose final commit escaped leaves no worker envelope on its branch, so inspection's head or ancestry fails.
A partial committed escape (some of the worker's commits on the base branch, the rest on its branch) is caught today
only by the Host's equality or by integration's `WORKTREE_MERGE_NOT_FF` refusal. Once
`PROP-integration-merge-moved-target` lands, integration merges a conflict-free moved target itself, so that refusal
no longer catches it, and review sees only the worker's range.

## 2. Decision Drivers

- A worker write outside its worktree must not stay hidden; a defect that surfaces later in CI, integration or
  hygiene is acceptable.
- Host integrations and other sessions' commits must not wait for a running worker.
- No per-integration declaration and no record that only the Host's conversation holds.
- The worker's own write audit (ancestry, changed paths in scope, clean worktree) stays as it is.

## 3. Considered Options

| Option | Trade-off |
| --- | --- |
| Keep the HEAD equality | Detects every escape; serializes every advance and needs a conversation-only record |
| Drop the equality; audit only the worker's range and dirty state | No ceremony or code; a partial committed escape lands unreviewed once integration merges moved targets |
| Host declares its own advances; any other advance stops | Detects every escape; one declaration per integration, a durable pre-spawn record, and a foreign-session commit still stops validation |
| Derived scope-overlap warning | No record and no Host step unless a base commit touches the worker's write scope; an escape outside the write scope goes unnamed |

`MAT-base-observation-options` holds the failure traces.

## 4. Decision Outcome

Chosen: the derived scope-overlap warning, because it keeps escape detection for the writes a worker makes (its write
scope) without serializing other advances or adding a record.

- **Window**: `devkit spec worker inspect` lists the non-merge commits reachable from the base checkout's HEAD and not
  from the returned head (`git rev-list --no-merges <base HEAD> --not <returned>`) whose committer time is at or after
  the committer time of the audit base `<accepted>`. Each commit contributes its own changed paths, so an escape is
  named by itself whatever merge carried it onto the base branch.
- **Overlap**: a window commit or a base-checkout dirty path inside the inspection's write scope is an entry of
  `base_checkout.overlap` and raises the `WARNING` `SPEC_WORKER_BASE_OVERLAP`. It fails no check: the exit code is `0`,
  and `1` only under `--strict`.
- **Accounting**: the Host accounts for a commit entry only when it made the commit itself or integrated a source that
  contains it (`git merge-base --is-ancestor <commit> <integrated source head>`), and for a dirty entry only when it
  wrote the path. Any other entry blocks the range unless the user confirms it as another session's write.
- The Host no longer records the base checkout before spawning and no longer requires its HEAD or status unchanged.
- Window commits outside the write scope are counted, not listed, and need no Host step. Dirty paths outside the write
  scope are left to integration's dirty-base refusal.
- A window that cannot be derived leaves the overlap not computed with a `SPEC_WORKER_CHECK_NOT_RUN` notice; it never
  makes inspection exit `2`.
- No base merge is required before validation; `PROP-integration-merge-moved-target` decides when the Host merges.

## 5. Consequences

- Positive: independent integrations and foreign commits proceed while a worker runs; the warning names the realistic
  escape (a worker writing its own task paths) and real collisions on the same paths.
- Negative: an escape commit that touches only paths outside the write scope is not named at validation; it reaches CI
  like any base commit. It needs both an out-of-scope `git add` and a commit in the wrong cwd.
- Negative: an in-scope commit from another session needs the user's confirmation, because Git cannot tell it from a
  worker's escape.
- The window relies on committer times on one machine; a base commit with a committer time before `<accepted>` is
  outside it.
- Follow-up trigger: if an escape outside the write scope is observed, list every window commit or add a commit-gate
  branch check.

## 6. Confirmation

- `packages/devkit-spec/tests/integration/features/worker/test_worker_inspect.py`: the proposal's WAH rows (in-scope
  commit, pre-audit-base commit, dirty paths, an escape carried by a merge, not-run scope, underivable window).
- `packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py`: `spec-delegate/references/worker.md`
  carries the accounting rule and neither it nor `payload.md` requires a pre-spawn base record.
- `devkit rules check` on `CAP-DLV-delivery-workflows` with the new code row.
