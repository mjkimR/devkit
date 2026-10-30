---
id: PROP-git-operator-result-readiness
title: Separate effect, readiness, permission and next actor in git-operator results
summary: "Make the composed handoff commit its own transaction and make git-operator results keep the original CLI result, worker-input readiness with exact dirty paths, host-permission blockers and the next actor distinct, so an uncommitted transaction is never read as clean worker input."
status: reviewing
created_at: 2026-10-30
target_area: capabilities/delivery/
priority: high
size: M
planning_effort: medium
dev_effort: medium
milestone: MS-git-operator-lifecycle-refinement
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/git-operator.md
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-next/references/
    - packages/devkit-spec/src/devkit_spec/features/delivery/
    - packages/devkit-spec/src/devkit_spec/features/proposals/
    - packages/devkit-spec/src/devkit_spec/base/
    - packages/devkit-spec/tests/
    - docs/capabilities/delivery/
  excludes:
    - .devkit/managed/
    - packages/devkit-core/
    - docs/capabilities/worktree/
task_kind: feature
decomposed_from: PROP-git-operator-pilot-follow-up
workflow: sdd-proposal
---

# [PROP-git-operator-result-readiness] Separate effect, readiness, permission and next actor in git-operator results

## 1. Background & Hypothesis

The resource-indexer consumer pilot reused one named `git-operator` for six worktree preparations and one
Development handoff (`MAT-git-operator-consumer-pilot`, held by this proposal). All seven guarded operations returned
exit 0 and the Host checked their effects. The operator kept operational details outside the Host context and
returned refs, paths and remaining effects. The pilot has not established a net token, cost or latency benefit.

A successful handoff left a known generated transaction uncommitted. CLI effect completion did not by itself mean
clean committed worker input, and the return named no uniform owner of the next action. This repository repeated it
on 2026-10-30: four composed handoffs (through `accept --mode accept_and_handoff` and the operator's `handoff`) left
the transaction uncommitted, and the Host committed each with one commit of every changed path
(`MAT-git-operator-handoff-commit-evidence`). One of them also carried a rewrite of a sibling draft that was in its own
Planning, which later conflicted (`FB-handoff-rewrite-edits-sibling-draft`).

The first actual integration request in the pilot was denied by automatic approval review before CLI execution. The
Host preserved resources and obtained explicit authorization for the named merge and cleanup effects; the same
guarded route, freshly prepared, then completed five Planning merges and their cleanup. This is observed
host-permission recovery, not evidence that policy-derived readiness grants host permission.

The hypothesis: when the composed handoff commits its own transaction and the operator result keeps the four facts
apart, the Host accepts or continues without re-deriving them and without a manual commit step.

## Source feedback

- `FB-handoff-rewrite-edits-sibling-draft`: received whole. The handoff leaves a sibling proposal that has its own
  `plan-<slug>` branch out of the reference rewrite and reports it as a pending rewrite.

## 2. Technical Spike Questions

- **Q1 Result shape**: How does a return distinguish requested effect completion, verified worker readiness, known
  dirty or generated outputs, and the next actor's work? CLI readiness stays separate from host execution
  permission. The three role statuses and the original CLI exit and effects stay, including a null CLI result when
  approval blocked dispatch.
  - **Answer**: two fields join the existing return. `worker_input` carries `state` (`ready`, `not_ready` or
    `not_applicable`), the observed `head` and the exact `dirty_paths`; `next_actor` names `host`, `implementer`,
    `worker` or `none` with one action line. Host permission needs no field: a denial before dispatch stays a
    blocker code with a null `cli_result`, and CLI readiness or `auto` policy is never reported as host permission.
- **Q2 Handoff interface**: Does the selected design change the handoff or setup interface? `CAP-WT-task-worktrees`
  changes only if it does; a successful uncommitted transaction is not reclassified as a failed CLI operation.
  - **Answer**: the composed handoff gains a commit step (`PADR-composed-handoff-commits-its-own-transaction`); its
    contract lives in `CAP-DLV-proposal-incubation`. Worktree start and setup do not change, so
    `CAP-WT-task-worktrees` stays as it is. The plain `handoff <slug>` stays write-only.

## 3. Proposed Design & Impact

### 3.1 Composed handoff commit (CLI)

- `HandoffUseCase._execute` (`features/delivery/usecases/native_handoff.py`) commits after the handoff and scope
  registration succeed, as `PADR-composed-handoff-commits-its-own-transaction` decides: one commit
  `spec: hand off <slug> to Development` whose single parent is the reviewed base head, HEAD reported after hooks.
- The result gains `commit` (the post-hook HEAD, or `null` when no commit landed). `[HANDOFF: ...]` adds
  `commit=<sha>`. `accept --mode accept_and_handoff` inherits the step through the same use case.
- A commit-gate refusal is a stopped handoff: `status: needs_recovery`, exit `1`, a new
  `SPEC_HANDOFF_COMMIT_REFUSED` error carrying the gate output and the dirty paths as `[TARGET]`, the writes kept.
  The `[NEXT_ACTION]` tells the Host to fix what the gate reports in the `dev-<slug>` worktree and commit.

### 3.2 Sibling drafts in the reference rewrite

- The handoff rewrite skips `docs/proposals/PROP-<other>/` files whose proposal has a `plan-<other>` branch and lists
  them in a pending-rewrite notice, so no file owned by another Planning branch enters the handoff commit.
- After that Planning merges, the existing reference repair (`devkit rules fix`) rewrites the stale citation.

### 3.3 git-operator result and Host acceptance

- `git-operator.md` adds `worker_input` and `next_actor` to the return. For `prepare-worktree` and `handoff` the
  operator fills `worker_input` from `git -C <worktree> status --porcelain` and `rev-parse HEAD`; `ready` requires a
  clean worktree whose HEAD is the reported commit. Other operations report `not_applicable`.
- `completed` keeps its meaning (every requested effect and check verified). A `handoff` whose CLI exited 0 but left
  dirty paths is not `ready`; it is never reported as a failed CLI operation.
- `git-operator-dispatch.md` makes the Host check `worker_input` against its own Git observation before starting a
  worker and follow `next_actor`; an exit code alone never stands for ready input.
- `git-operator-operations.md` names the handoff's `commit` and the pending-rewrite notice in the `handoff` row.
- `CAP-DLV-delivery-workflows` §4.6.1 lists the two fields and their checks; `CAP-DLV-proposal-incubation` states the
  composed handoff commit, the refusal code and the sibling skip. The `spec` skill's worktree reference and the
  post-handoff link check drop the implied Host commit.

Evidence stays separated: CLI exit and effects, role status, actual Git observations, host emulation and remaining
work. Host-permission denial and reauthorization are observations, not reusable approval credentials.

### 3.4 Acceptance checks

| ID | Given | When | Then |
| --- | --- | --- | --- |
| GOP-02 | A composed handoff in a clean new worktree | It completes | One commit whose parent is the reviewed base holds the whole transaction, the worktree is clean, and the result reports the post-hook HEAD; the operator returns `worker_input.state: ready` with that head. |
| GOP-02b | A composed handoff whose commit the gate refuses | It stops | Exit `1`, `SPEC_HANDOFF_COMMIT_REFUSED`, the writes kept with exact dirty paths; the operator returns the original CLI result, `worker_input.state: not_ready` with those paths and `next_actor: host`. |
| GOP-03 | A sibling proposal with its own `plan-<other>` branch cites the handed-off proposal | The handoff rewrites references | The sibling file is unchanged and listed as a pending rewrite. |
| GOP-06 | A request for production edits, semantic conflict resolution or broader authority | The operator receives the job | It returns that work to the Host or implementer and performs no such mutation. |
| GOP-07 | Mixed live integration, host-refusal recovery and untested failure cases | Reports are updated after actual observations | Live effects, null CLI result on pre-dispatch denial, isolated fixtures, replays and untested cases remain separate; unknown cost or latency is not reported as an improvement. |

GOP-02, GOP-02b and GOP-03 are integration tests under `packages/devkit-spec/tests/integration/features/`; GOP-06 and
GOP-07 are contract-text tests in `packages/devkit-spec/tests/integration/bundles/spec/test_git_operator.py` plus
review.

### Non-goals

- **Scope Excluded**: operator source authoring, semantic decisions, approval grants, force operations or arbitrary
  remote deletion.
- **Scope Excluded**: changing policy or bypassing a host refusal to make a lifecycle operation succeed.
- **Scope Excluded**: new model routing, universal native-host guarantees or unmeasured token, cost or latency savings.
- **Scope Excluded**: a commit in the plain `devkit spec proposal handoff <slug>`, a configurable commit subject or a
  rollback of a refused handoff.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-git-operator-result-readiness`; the proposal is deleted there, its decisions become ADRs and its materials move
  to `docs/materials/`.
- On Rejection: `status: rejected` only, with the user's reason in the commit message. Before the proposal is
  deleted, move `MAT-git-operator-consumer-pilot` to `docs/materials/` so the sibling proposals' citations resolve.
