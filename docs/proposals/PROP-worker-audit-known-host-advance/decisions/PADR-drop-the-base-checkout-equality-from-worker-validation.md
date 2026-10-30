---
id: PADR-drop-the-base-checkout-equality-from-worker-validation
title: Drop the base-checkout equality from worker validation
summary: For worker validation, we drop the base-checkout status and HEAD equality and its pre-spawn record and require each turn to add its own worker envelope, so integrations need not wait for a worker, accepting that a partial committed escape can stay hidden.
proposal: PROP-worker-audit-known-host-advance
status: draft
created_at: 2026-10-30
---

# [PADR-drop-the-base-checkout-equality-from-worker-validation] Drop the base-checkout equality from worker validation

- **Status**: Draft
- **Date**: 2026-10-30

---

## 1. Context & Problem Statement

A worker's default cwd may be the base checkout (`ADR-orchestration-workers`, Codex native worker execution), so a
relative-path write or a commit can escape its worktree, outside the audited range `<accepted>..<returned>`. The Host
detects that by recording the base checkout's status and HEAD before spawning and requiring both unchanged at
validation (`ADR-orchestration-workers`, committed results and their validation). The same equality stops on every
Host integration and every commit another session makes to the base branch, so the Host serialized independent
integrations behind a running worker (`MAT-git-operator-consumer-pilot`). The pre-spawn record lives only in the
Host's conversation.

Existing checks catch most escapes once one condition is explicit. A dirty base checkout refuses handoff
(`SPEC_HANDOFF_BASE_DIRTY`) and integration (`WORKTREE_BASE_DIRTY`). A full escape (the whole turn, its `worker`
envelope included, committed in the base) fails only if the Host requires `<returned>` to add this turn's envelope:
inspection derives `head` from the latest envelope on the branch, so on a later turn it re-audits the previous turn
and passes. A partial committed escape (some worker commits on the base branch) passes every check: today's
`WORKTREE_MERGE_NOT_FF` fix merges the base into the branch without naming any commit.

## 2. Decision Drivers

- A worker write outside its worktree must not stay hidden; a defect that surfaces later in CI, integration or
  hygiene is acceptable.
- Host integrations and other sessions' commits must not wait for a running worker.
- Lifecycle checks stay light: no per-integration declaration, no conversation-only record and no new mechanism
  without an observed failure.
- The worker's own write audit (ancestry, changed paths in scope, clean worktree) stays as it is.

## 3. Considered Options

| Option | Trade-off |
| --- | --- |
| Keep the HEAD equality | Detects every escape; serializes every advance and needs a conversation-only record |
| Drop the equality and its record; require the turn's own envelope | No ceremony and no code; a partial committed escape whose content passes CI stays hidden |
| Host declares its own advances; any other advance stops | Detects every escape; one declaration per integration, a durable pre-spawn record, and a foreign-session commit still stops validation |
| Derived scope-overlap warning in inspection | Names in-scope base commits without a record; a time-bounded window drops escapes because committer times do not follow ancestry, and a topology-only window repeats other units' commits for accounting or user confirmation |

`MAT-base-observation-options` holds the failure traces and the review history of the warning.

## 4. Decision Outcome

Chosen: drop the equality and its pre-spawn record and require the turn's own envelope, because the remaining
checks name every escape except a partial committed one, and each mechanism that also names that case adds recurring
Host or user work. The partial committed escape is an accepted exception to the first driver.

- The Host no longer records the base checkout before spawning and no longer requires its status or HEAD unchanged
  at validation.
- The range passes when `<returned>` adds this turn's `worker` envelope (absent at `<accepted>`), plus the existing
  ancestry, worktree HEAD, write-scope, clean-worktree and check conditions.
- `devkit spec worker inspect` keeps reporting the base checkout's HEAD and dirty paths as information.
- Base advances by the Host, another session or an unknown author never block a worker's range; no base merge is
  required before validation.
- This decision supersedes two clauses of `ADR-orchestration-workers`: in committed results and their validation,
  "and the base checkout unchanged"; in informational range inspection, "comparing them with what the Host recorded
  before spawning stays the Host's step". The rest of that ADR stays in force.

## 5. Consequences

- Positive: independent integrations and foreign commits proceed while a worker runs; the Host drops one record and
  one comparison per worker.
- Negative: a partial committed escape (a worker committing some work on the base branch through the wrong cwd) is
  named by no check. If its content passes CI, nobody reviews or attributes it, so it stays hidden. It needs several
  commands of one turn to miss the worktree cwd; none has been observed.
- Follow-up trigger: if such an escape is observed, add a commit-gate check that refuses a commit in the base checkout
  touching a path an active task worktree's unit owns (`CAP-COLL-work-scope-registry`), or revisit the overlap warning.

## 6. Confirmation

- `packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py`: `spec-delegate/references/worker.md`
  and `payload.md` carry no pre-spawn base record and no unchanged-base requirement; `worker.md` requires the turn's
  own envelope and keeps the remaining range conditions.
- The reconcile review checks that `CAP-DLV-delivery-workflows`' acceptance requirements name the turn's own `worker`
  envelope instead of an unchanged base and its base-checkout observation names no Host comparison, that the promoted
  ADR names the two superseded clauses and that `ADR-orchestration-workers` points to it.
