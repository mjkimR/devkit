---
id: PADR-replace-the-base-head-equality-with-a-scope-overlap-notice
title: Replace the base HEAD equality with a scope-overlap notice
summary: For worker validation, we replace base-checkout HEAD equality with a notice naming base commits after the audit base and base dirty paths inside the write scope, to keep detecting worker escapes without serializing other advances, accepting that out-of-scope escapes go unnamed.
proposal: PROP-worker-audit-known-host-advance
status: draft
created_at: 2026-10-30
---

# [PADR-replace-the-base-head-equality-with-a-scope-overlap-notice] Replace the base HEAD equality with a scope-overlap notice

- **Status**: Draft
- **Date**: 2026-10-30

---

## 1. Context & Problem Statement

A worker's default cwd may be the base checkout (`ADR-orchestration-workers`, Codex native worker execution), so a relative-path write or a
commit can escape its worktree, outside the audited range `<accepted>..<returned>`. The Host detects that by recording
the base checkout's status and HEAD before spawning and requiring both unchanged at validation
(`ADR-orchestration-workers`, committed results and their validation). The same equality stops on every Host integration and every commit another
session makes to the base branch, so the Host serialized independent integrations behind a running worker
(`MAT-git-operator-consumer-pilot`). The pre-spawn HEAD lives only in the Host's conversation, and
`devkit spec worker inspect` reports the base checkout as information only
(`ADR-orchestration-workers`, informational range inspection).

Once `PROP-integration-merge-moved-target` lands, integration merges a conflict-free moved target itself, so a commit
that escaped onto the base branch is no longer stopped at integration either. A dirty escape still surfaces there,
because integration refuses a dirty base checkout (`WORKTREE_BASE_DIRTY`).

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
| Drop the equality; audit only the worker's range and dirty state | No ceremony; a committed escape stays hidden once integration merges moved targets |
| Host declares its own advances; any other advance stops | Detects every escape; one declaration per integration, a durable pre-spawn record, and a foreign-session commit still stops validation |
| Derived scope-overlap notice | No record and no ceremony unless an advance touches the worker's scope; an escape outside the write scope goes unnamed |

`MAT-base-observation-options` holds the failure traces.

## 4. Decision Outcome

Chosen: the derived scope-overlap notice, because it keeps escape detection for the writes a worker makes (its write
scope) without serializing other advances or adding a record.

- `devkit spec worker inspect` derives a window: the first-parent commits of the base checkout's HEAD after its merge
  base with the returned head, committed after the audit base `<accepted>`. Each commit contributes its first-parent
  changed paths.
- A window commit or a base-checkout dirty path inside the inspection's write scope is reported in
  `base_checkout.overlap` and raises the `NOTICE` `SPEC_WORKER_BASE_OVERLAP`; its `[ACTION]` tells the Host to confirm
  each entry is its own or another session's write and otherwise block the range. The notice fails no check; the
  exit code changes only under `--strict`.
- The Host no longer records the base checkout before spawning and no longer requires its HEAD or status unchanged.
  It accepts a range only after accounting for every overlap entry; an unaccounted entry is a block.
- Advances outside the write scope are counted, not listed, and need no Host step. Dirty paths outside the write scope
  are left to integration's dirty-base refusal.
- No base merge is required before validation; `PROP-integration-merge-moved-target` decides when the Host merges.

## 5. Consequences

- Positive: independent integrations and foreign commits proceed while a worker runs; the notice names the realistic
  escape (a worker writing its own task paths) and real collisions on the same paths.
- Negative: an escape commit that touches only paths outside the write scope is not named at validation; it reaches CI
  and later review like any base commit. It needs both an out-of-scope `git add` and a commit in the wrong cwd.
- Negative: broad `_Boundary:` prefixes can make another unit's integration overlap; the Host accounts for it once per
  inspection.
- The window depends on committer times on one machine; a base commit made with a committer time before `<accepted>`
  is outside the window.
- Follow-up trigger: if an out-of-scope escape is observed, add a whole-window listing or a commit-gate branch check.

## 6. Confirmation

- `packages/devkit-spec/tests/integration/features/worker/test_worker_inspect.py`: an in-scope base commit after the
  audit base and an in-scope dirty path raise `SPEC_WORKER_BASE_OVERLAP` with exit `0`; an out-of-scope advance, an
  advance before the audit base and an out-of-scope dirty path raise none; a not-run scope computes no overlap.
- `packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py`: `spec-delegate/references/worker.md`
  carries the overlap accounting and no pre-spawn record.
- `devkit rules check` on `CAP-DLV-delivery-workflows` with the new code row.
