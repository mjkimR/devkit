---
id: PROP-git-operator-result-readiness
title: Separate effect, readiness, permission and next actor in git-operator results
summary: "Make the composed handoff commit its own transaction and make git-operator results report worker-input readiness with exact dirty paths apart from the original CLI result and host-permission blockers, so an uncommitted transaction is never read as clean worker input."
status: accepted
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
    - docs/usecases/delivery/
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

The hypothesis: when the composed handoff commits its own transaction and the operator result reports worker-input
readiness from Git observation, the Host continues without re-deriving it and without committing the handoff
transaction itself.

## Source feedback

- `FB-handoff-rewrite-edits-sibling-draft`: addressed directly by this proposal (§3.2); it stays open until
  Development verifies the fix and resolves it. The handoff keeps
  rewriting a sibling draft's references (its `depends_on` rewrite is a MUST that keeps later handoffs valid); the
  guidance names the resolution of the later base-merge conflict instead.

## 2. Technical Spike Questions

- **Q1 Result shape**: How does a return distinguish requested effect completion, verified worker readiness, known
  dirty or generated outputs, and the next actor's work? CLI readiness stays separate from host execution
  permission. The three role statuses and the original CLI exit and effects stay, including a null CLI result when
  approval blocked dispatch.
  - **Answer**: no new top-level field. For `prepare-worktree` and `handoff` the operator reports
    `checks.worker_input` with the observed `head` and exact `dirty_paths`. A dirty path is also a
    `remaining_effects` entry, so the result is `needs_input`, never `completed`. The next action is the Host's:
    the operator always returns to the Host, which owns scheduling, and `remaining_effects` names the work. Host
    permission needs no field: a denial before dispatch stays a blocker code with a null `cli_result`, and CLI
    readiness or `auto` policy is never reported as host permission.
- **Q2 Handoff interface**: Does the selected design change the handoff or setup interface? `CAP-WT-task-worktrees`
  changes only if it does; a successful uncommitted transaction is not reclassified as a failed CLI operation.
  - **Answer**: the composed handoff gains a commit step (`PADR-composed-handoff-commits-its-own-transaction`); its
    contract lives in `CAP-DLV-proposal-planning`. Worktree start and setup do not change, so
    `CAP-WT-task-worktrees` stays as it is. The plain `handoff <slug>` stays write-only.

## 3. Proposed Design & Impact

### 3.1 Composed handoff commit (CLI)

- `HandoffUseCase._execute` (`features/delivery/usecases/native_handoff.py`) commits after the handoff and scope
  registration succeed, as `PADR-composed-handoff-commits-its-own-transaction` decides: one commit
  `spec: hand off <slug> to Development` of the delta `git status` reports (the handoff result does not list the
  removed proposal files), whose single parent is the reviewed base head, with HEAD read after `git commit` returns.
- The result gains `commit` (that HEAD, or `null` when no commit landed). `[HANDOFF: ...]` adds `commit=<sha>`.
  `accept --mode accept_and_handoff` inherits the step through the same use case, records the handoff step in
  `completed_steps` whenever the handoff writes landed, and carries `commit`.
- A refused commit (any `git commit` failure: the gate, a missing identity, signing) is a stopped handoff:
  `status: needs_recovery`, exit `1`, a new `SPEC_HANDOFF_COMMIT_REFUSED` error with the commit output and the dirty
  paths as `[TARGET]`, the writes kept. The result carries no `next_command`; its `[NEXT_ACTION]` tells the Host to
  fix what the commit output reports in the `dev-<slug>` worktree and commit there.

### 3.2 Sibling drafts in the reference rewrite

- The rewrite is unchanged: a sibling draft's `depends_on` and ID references to the handed-off proposal are rewritten,
  because a skipped `depends_on` dangles once the dev branch lands and makes every later handoff refuse.
- `CAP-DLV-proposal-planning` and the post-handoff link check name the resolution of the conflict this causes when
  the sibling's Planning merges first: on a base-merge conflict in a file under `docs/proposals/PROP-<other>/`, take
  the base version and run `devkit rules fix` on it, which rewrites the citation (`PROP-<slug> was handed off`).

### 3.3 git-operator result and Host acceptance

- `git-operator.md` defines `checks.worker_input: {head, dirty_paths}` for `prepare-worktree` and `handoff`, filled
  from `git -C <worktree> status --porcelain` and `rev-parse HEAD`. Non-empty `dirty_paths` also appear in
  `remaining_effects`; the result is then `needs_input`. A CLI exit 0 with dirty paths is never reported as a failed
  CLI operation or as ready input.
- `git-operator-dispatch.md` makes the Host compare `checks.worker_input` with its own Git observation before starting
  a worker; an exit code alone never stands for ready input.
- `git-operator-operations.md` names the handoff's `commit` and `checks.worker_input` in the `handoff` row.
- Post-handoff link fixes: when the handoff result carries `[UNRESOLVED_LINK]` or `[REWRITTEN ...]` lines outside the
  new spec and promoted ADRs, the Host runs the post-handoff link check and commits its fixes before starting a
  worker. The `spec` skill's worktree reference and `post-handoff.md` say so in place of "the same change".
- `CAP-DLV-delivery-workflows` §4.6.1 states the `worker_input` check. `CAP-DLV-proposal-planning` states the
  composed handoff commit, `SPEC_HANDOFF_COMMIT_REFUSED`, the sibling conflict resolution, and narrows "handoff does
  not create a commit" to the plain form. `UC-plan-and-hand-off-a-proposal` updates step 9 (link fixes in a Host
  commit after the handoff commit) and extension 7a (the refused-commit stop).

Evidence stays separated: CLI exit and effects, role status, actual Git observations, host emulation and remaining
work. Host-permission denial and reauthorization are observations, not reusable approval credentials.

### 3.4 Acceptance checks

| ID | Given | When | Then |
| --- | --- | --- | --- |
| GOP-02 | A composed handoff in a clean new worktree | It completes | One commit whose single parent is the reviewed base holds the whole transaction, the worktree is clean, and `commit` equals HEAD read after the hooks. |
| GOP-02b | A composed handoff whose commit is refused | It stops | Exit `1`, `[HANDOFF_STOPPED ...]`, `SPEC_HANDOFF_COMMIT_REFUSED` with the dirty paths, the writes kept, `[NEXT_ACTION]` and no `[NEXT_CMD]`; under `accept_and_handoff` `completed_steps` includes the handoff. |
| GOP-02c | The git-operator contract | A `handoff` or `prepare-worktree` result is returned | `checks.worker_input` carries `head` and `dirty_paths`; dirty paths are `remaining_effects` and never `completed`; the Host compares them with its own Git observation before starting a worker. |
| GOP-06 | A request for production edits, semantic conflict resolution or broader authority | The operator receives the job | It returns that work to the Host and performs no such mutation. |
| GOP-07 | Mixed live integration, host-refusal recovery and untested failure cases | Reports are updated after actual observations | Live effects, null CLI result on pre-dispatch denial, isolated fixtures, replays and untested cases remain separate; unknown cost or latency is not reported as an improvement. |
| GOP-09 | A sibling draft in its own Planning cites the handed-off proposal | The handoff rewrites references and the guidance is read | The sibling's `depends_on` is rewritten, and `CAP-DLV-proposal-planning` and `post-handoff.md` name the take-base-then-`devkit rules fix` resolution. |

GOP-02 and GOP-02b are CLI integration tests under `packages/devkit-spec/tests/integration/features/delivery/` (a
rewriting post-commit hook and a refusing pre-commit hook in the fixture repository). GOP-02c, GOP-06, GOP-07 and
GOP-09 are contract-text tests in `packages/devkit-spec/tests/integration/bundles/spec/test_git_operator.py` (and the
bundle text tests for `post-handoff.md`) plus review.

### 3.5 Planning decisions

- The user chose the composed handoff commit over a Host commit step or a commit in every handoff (§3.1,
  `PADR-composed-handoff-commits-its-own-transaction`), readiness under `checks.worker_input` with no new top-level
  field and no `next_actor` (§3.3), and an unchanged reference rewrite with guidance only over a sibling skip (§3.2).
- The Host assigned the shared GOP-06 operator-scope wording to this proposal: an operator returns production edits,
  semantic conflict resolution and broader authority to the Host. `git-operator.md` keeps that wording in its
  authority section; `PROP-git-operator-planning-completion-route` and `PROP-git-operator-batch-preparation` keep
  GOP-06 only as a regression check and do not reword it.
- `PROP-git-operator-batch-preparation` reports each item with the §3.3 result shape (`checks.worker_input`,
  dirty paths in `remaining_effects`) and adds no field of its own.
- Development of this proposal and its sibling git-operator proposals integrates one at a time in dependency order,
  so each later sibling rebuilds on the integrated `git-operator.md`, `spec-orchestrate` and delivery capability text.

### Non-goals

- **Scope Excluded**: operator source authoring, semantic decisions, approval grants, force operations or arbitrary
  remote deletion.
- **Scope Excluded**: changing policy or bypassing a host refusal to make a lifecycle operation succeed.
- **Scope Excluded**: new model routing, universal native-host guarantees or unmeasured token, cost or latency savings.
- **Scope Excluded**: a commit in the plain `devkit spec proposal handoff <slug>`, a configurable commit subject, a
  rollback of a refused handoff, or skipping Planning-owned siblings in the reference rewrite.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-git-operator-result-readiness`; the proposal is deleted there, its decisions become ADRs and its materials move
  to `docs/materials/`.
- On Rejection: `status: rejected` only, with the user's reason in the commit message. Before the proposal is
  deleted, move `MAT-git-operator-consumer-pilot` to `docs/materials/` so the sibling proposals' citations resolve.
