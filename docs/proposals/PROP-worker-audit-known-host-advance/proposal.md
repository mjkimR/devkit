---
id: PROP-worker-audit-known-host-advance
title: Stop requiring an unchanged base checkout in worker validation
summary: "Drop the base-checkout HEAD and status equality from worker validation and require each returned turn to add its own worker envelope, so integrations and other sessions need not wait for a running worker; a partial committed escape into the base is an accepted residual."
status: reviewing
created_at: 2026-10-30
target_area: capabilities/delivery/
priority: medium
size: S
planning_effort: high
dev_effort: medium
milestone: MS-git-operator-lifecycle-refinement
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/
    - docs/decisions/2026-10/20261022-orchestration-workers.md
    - packages/devkit-spec/tests/
    - docs/capabilities/delivery/
  excludes:
    - .devkit/managed/
    - packages/devkit-core/
task_kind: feature
decomposed_from: PROP-git-operator-pilot-follow-up
workflow: sdd-proposal
---

# [PROP-worker-audit-known-host-advance] Stop requiring an unchanged base checkout in worker validation

## 1. Background & Hypothesis

The exact-base observation rule caused unnecessary serialization in the resource-indexer consumer pilot
(`MAT-git-operator-consumer-pilot`): the Host held independent Planning integrations while a Development worker ran,
solely to preserve its recorded base HEAD. The worker reference (`spec-delegate/references/worker.md`) requires the
base checkout's status and HEAD to match the pre-spawn record; `devkit spec worker inspect` only reports the base
checkout's HEAD and dirty paths as information.

The equality exists to catch a worker write that escapes into the base checkout, because a worker's default cwd may
be the base checkout (`MAT-base-observation-options`). In this repository on 2026-10-30, another session committed
to `main` while a Development worker ran; the Host validated the range with `devkit spec worker inspect --base
<accepted>` without issue.

The hypothesis: the worker's own range audit, one explicit envelope condition and the existing dirty-base refusals
name every worker escape except a partial committed one, so the equality can go without a replacement mechanism. The
user accepted that residual (`answer-01`).

## 2. Technical Spike Questions

- **Q1 Declaration**: How does the Host declare a target advance as its own, and how does inspection verify it?
  Answer: no declaration. The rule protects against a worker write escaping into the base checkout, not against
  advances. A declaration list costs one record per integration plus a durable pre-spawn HEAD, and it still stops on
  another session's commit (`MAT-base-observation-options`, option B).
- **Q2 Boundary**: Which changes still stop the worker? Answer: everything the worker audit checks today (ancestry,
  head, changed paths outside scope, dirty worktree, envelopes, rules and workflow), plus one explicit condition.
  Base advances never stop validation. Escapes surface as follows:
  - A full escape (the whole turn, its `worker` envelope included, committed in the base checkout): the new condition
    "`<returned>` adds this turn's `worker` envelope, absent at `<accepted>`" fails. Inspection alone does not catch it
    on a later turn, because it derives `head` from the latest envelope on the branch and re-audits the previous turn
    (`challenger-03` finding 1).
  - An uncommitted write in the base checkout: handoff refuses (`SPEC_HANDOFF_BASE_DIRTY`) and integration refuses
    (`WORKTREE_BASE_DIRTY`).
  - A partial committed escape (some worker commits on the base branch, the rest on its branch): no check names it,
    with or without `PROP-integration-merge-moved-target`. Today's `WORKTREE_MERGE_NOT_FF` fix merges the base without
    naming any commit, and after the sibling the integrating command merges a conflict-free moved target the same way.
    If its content passes CI, it stays hidden: nobody reviews or attributes it. The user accepted it as an exception to
    "a defect must not stay hidden". It needs several commands in one turn to miss the worktree cwd; none has been
    observed.
- **Q3 Interaction with light merging**: no base merge is required before validation or acceptance; nothing in this
  proposal reads the base checkout's HEAD.

## 3. Proposed Design & Impact

`PADR-drop-the-base-checkout-equality-from-worker-validation` records the decision: the user chose dropping the
equality (option A in `MAT-base-observation-options`).

- **Host procedure** (`spec-delegate/references/worker.md`, `payload.md`): drop the pre-spawn record of the base
  checkout's status and HEAD and the requirement that both match. Add the condition that `<returned>` adds this
  turn's `worker` envelope, absent at `<accepted>`. The range passes on that condition and the existing ones:
  ancestry, worktree HEAD, changed paths in the write scope, a clean worktree and the unit's checks. Host
  integrations and other sessions' commits proceed while a worker runs.
- **Inspection**: `devkit spec worker inspect` is unchanged; `base_checkout` stays an observation.
- **Contract**: `CAP-DLV-delivery-workflows` replaces "unchanged base" among the acceptance requirements with the
  turn's own `worker` envelope and words the base checkout observation as information with no Host comparison. A new ADR supersedes the base-checkout clauses of
  `ADR-orchestration-workers` (committed results and their validation; informational range inspection), and that ADR
  gains a one-line pointer to it. `ADR-reusable-lifecycle-resource-manager` keeps the write audit with the Host
  unchanged.
- **Unchanged**: the worker audit range `<accepted>..<returned>`, its checks and exit codes; Host and foreign commits
  never enter `changed_paths`; integration's dirty-base refusal; completed specs and earlier materials that restate
  the equality stay as history.
- **Follow-up trigger**: if a partial committed escape is ever observed, the follow-up is a commit-gate check that
  refuses a base-checkout commit touching a path an active task worktree's unit owns. No follow-up draft is filed
  before that.

### Acceptance

| ID | Given | When | Then |
| --- | --- | --- | --- |
| GOP-08 | An audit base A, base commits B made after spawning (Host, foreign or unknown), and a returned head C | The Host validates the worker's result with `devkit spec worker inspect` | A..C is the audited range with its existing checks; B never enters `changed_paths` or `outside_scope` and never blocks the range; a dirty base checkout and real conflicts stop at handoff or integration through their existing refusals. |
| WAH-01 | The bundle's worker and payload references | `test_role_contracts.py` runs | Neither `worker.md` nor `payload.md` requires a pre-spawn base record or an unchanged base status or HEAD; `worker.md` requires `<returned>` to add this turn's `worker` envelope, absent at `<accepted>`, and keeps the ancestry, HEAD, write-scope and clean-worktree conditions. |
| WAH-02 | `CAP-DLV-delivery-workflows`, the promoted ADR and `ADR-orchestration-workers` | The reconcile review of the Development unit checks them | `CAP-DLV-delivery-workflows`' acceptance requirements name the turn's own `worker` envelope instead of an unchanged base, and its base-checkout observation names no Host comparison; the promoted ADR names the two superseded clauses; `ADR-orchestration-workers` carries a pointer line to it. |

### Non-goals

- **Scope Excluded**: a global repository lock or autonomous scheduler.
- **Scope Excluded**: treating a base advance as worker authorship, write permission or a skip of the final
  integration checks.
- **Scope Excluded**: a declaration record of Host advances, a base-advance window in inspection, or a commit-gate
  branch check.
- **Scope Excluded**: changing integration's dirty-base refusal or its handling of moved targets
  (`PROP-integration-merge-moved-target`).

## Planning decisions

- Planning compared dropping the equality (A), a declared-Host-advance list (B) and a derived scope-overlap warning
  (C) (`MAT-base-observation-options`). It first recommended C; `challenger-01` and `challenger-02` showed that C's
  window either loses escapes or needs per-entry accounting, so Planning recommended A. The user chose A, accepted
  the partial committed escape as a stated exception and filed no follow-up draft (`answer-01`).
- GOP-08 is restated under A: the parent's "unknown or dirty target changes stop" would stop on every foreign commit;
  a dirty base and real conflicts stop at their existing refusals instead.
- The earlier scope-overlap-warning PADR was withdrawn with the switch to A and replaced by
  `PADR-drop-the-base-checkout-equality-from-worker-validation`.
- The new ADR names the superseded clauses in its text and `ADR-orchestration-workers` gets a pointer line; it carries
  no `supersedes` field, because superseding the alias of the committed-results decision in `ADR-orchestration-workers`
  would also retire the worker's Git actions and the rest of that decision.
- `size` is `S`: the change is the bundle references, one capability, one ADR and its pointer, and one contract test.
- `challenger-03` showed that inspection does not catch a full escape on a later turn and that the remaining residual
  can stay hidden; the envelope condition and the stated exception answer them.
- `spec-orchestrate/` left `owns`: its sequencing rule never relied on the base equality.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-worker-audit-known-host-advance`; the proposal is deleted there and its decisions become ADRs.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
