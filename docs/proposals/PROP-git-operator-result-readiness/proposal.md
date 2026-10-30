---
id: PROP-git-operator-result-readiness
title: Separate effect, readiness, permission and next actor in git-operator results
summary: "Make git-operator results keep the original CLI result and effects, host permission, worker-input readiness with exact dirty paths, and the next actor distinct, so an uncommitted handoff transaction is never read as clean committed worker input."
status: draft
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
    - packages/devkit-spec/src/devkit_spec/features/proposals/
    - packages/devkit-spec/tests/
    - docs/capabilities/delivery/
    - docs/capabilities/worktree/
  excludes:
    - .devkit/managed/
    - packages/devkit-core/
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
clean committed worker input, and the return named no uniform owner of the next action. This repository's run on
2026-10-30 repeated it: both handoffs (composed `accept_and_handoff` and a plain operator `handoff`) left the
transaction uncommitted, and the Host committed it before starting a worker.

The first actual integration request in the pilot was denied by automatic approval review before CLI execution. The
Host preserved resources and obtained explicit authorization for the named merge and cleanup effects; the same
guarded route, freshly prepared, then completed five Planning merges and their cleanup. This is observed
host-permission recovery, not evidence that policy-derived readiness grants host permission.

The hypothesis: a result that keeps these four facts apart lets the Host accept or continue without re-deriving them.

## 2. Technical Spike Questions

- **Q1 Result shape**: How does a return distinguish requested effect completion, verified worker readiness, known
  dirty or generated outputs, and the next actor's work? CLI readiness stays separate from host execution
  permission. The three role statuses and the original CLI exit and effects stay, including a null CLI result when
  approval blocked dispatch.
- **Q2 Handoff interface**: Does the selected design change the handoff or setup interface? `CAP-WT-task-worktrees`
  changes only if it does; a successful uncommitted transaction is not reclassified as a failed CLI operation.

## 3. Proposed Design & Impact

- The git-operator contract and spec-orchestrate acceptance guidance carry the result fields and the Host's check of
  each.
- `CAP-DLV-delivery-workflows` holds the result semantics; `CAP-WT-task-worktrees` only if Q2 changes the interface.
- Evidence stays separated: CLI exit and effects, role status, actual Git observations, host emulation and remaining
  work. Host-permission denial and reauthorization are observations, not reusable approval credentials.

Acceptance checks (from the parent's verification candidates):

| ID | Given | When | Then |
| --- | --- | --- | --- |
| GOP-02 | A successful handoff with generated uncommitted files | The operator returns its result | Original CLI success and effects, exact dirty paths, worker-readiness evidence and next-action owner are distinguishable; no clean committed input is implied. |
| GOP-06 | A request for production edits, semantic conflict resolution or broader authority | The operator receives the job | It returns that work to the Host or implementer and performs no such mutation. |
| GOP-07 | Mixed live integration, host-refusal recovery and untested failure cases | Reports are updated after actual observations | Live effects, null CLI result on pre-dispatch denial, isolated fixtures, replays and untested cases remain separate; unknown cost or latency is not reported as an improvement. |

### Non-goals

- **Scope Excluded**: operator source authoring, semantic decisions, approval grants, force operations or arbitrary
  remote deletion.
- **Scope Excluded**: changing policy or bypassing a host refusal to make a lifecycle operation succeed.
- **Scope Excluded**: new model routing, universal native-host guarantees or unmeasured token, cost or latency savings.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-git-operator-result-readiness`; the proposal is deleted there, its decisions become ADRs and its material moves
  to `docs/materials/`.
- On Rejection: `status: rejected` only, with the user's reason in the commit message. Before the proposal is
  deleted, move `MAT-git-operator-consumer-pilot` to `docs/materials/` so the sibling proposals' citations resolve.
