---
id: PROP-git-operator-batch-preparation
title: Bounded batch preparation for git-operator
summary: "Let the Host dispatch an exact finite list of independent worktree preparations with per-item identity, authority, effects, checks and outcome, keeping original CLI results for partial or denied items and retrying only inspected authorized remainders."
status: draft
created_at: 2026-10-30
target_area: capabilities/delivery/
priority: medium
size: M
planning_effort: medium
dev_effort: medium
milestone: MS-git-operator-lifecycle-refinement
depends_on: [PROP-git-operator-result-readiness]
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/git-operator.md
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/
    - packages/devkit-spec/src/devkit_spec/features/delivery/
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

# [PROP-git-operator-batch-preparation] Bounded batch preparation for git-operator

## 1. Background & Hypothesis

In the resource-indexer consumer pilot (`MAT-git-operator-consumer-pilot`), preparing five exact worktrees required an
ad hoc multi-job payload and an aggregate return under a role contract written for one job. The operations
succeeded; partial-batch behavior remains unverified. This repository's run on 2026-10-30 used one job per dispatch
through operator continuation, which is the baseline to compare against.

The hypothesis: an exact finite job list with per-item outcomes lowers dispatch overhead without losing per-item
identity, authority or recovery.

## 2. Technical Spike Questions

- **Q1 Mechanism**: Is a typed list of existing independent jobs in the role contract enough, or is a new CLI
  operation worth it? Compare dispatch and result size, permission overhead and failure recovery. CLI support may
  belong in `packages/devkit` (`devkit worktree start`); choosing it records a boundary extension in Planning.
- **Q2 Partial outcomes**: How does a batch stop or continue on a denied or partial item, and how does a retry target
  only the inspected, authorized remainder?

## 3. Proposed Design & Impact

- The git-operator contract and spec-orchestrate dispatch accept a bounded preparation list.
- Each item's result uses the result semantics `PROP-git-operator-result-readiness` defines, which is why this
  proposal depends on it.

Acceptance checks (from the parent's verification candidates):

| ID | Given | When | Then |
| --- | --- | --- | --- |
| GOP-05 | An authorized finite preparation list with one denied or partial item | A batch stops or continues within its stated policy | Each item's original CLI result and completed and remaining effects are retained; retries target only inspected authorized remainders. |
| GOP-06 | A request for production edits, semantic conflict resolution or broader authority | The operator receives the job | It returns that work to the Host or implementer and performs no such mutation. |

### Non-goals

- **Scope Excluded**: a daemon, global repository lock or autonomous scheduler.
- **Scope Excluded**: operator source authoring, approval grants, force operations or arbitrary remote deletion.
- **Scope Excluded**: unmeasured token, cost or latency savings.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-git-operator-batch-preparation`; the proposal is deleted there and its decisions become ADRs.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
