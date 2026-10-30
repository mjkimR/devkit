---
id: PROP-git-operator-planning-completion-route
title: Planning completion and acceptance execution route for git-operator
summary: "Define how a Planning run records its return when workflow next shows no current stage, and document the Host-record then operator-integration acceptance route, adding a composed acceptance job only if it measurably lowers Host burden."
status: draft
created_at: 2026-10-30
target_area: capabilities/delivery/
priority: high
size: M
planning_effort: medium
dev_effort: low
milestone: MS-git-operator-lifecycle-refinement
depends_on: [PROP-integration-merge-moved-target]
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/git-operator.md
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-review-proposal/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/workflows/
    - packages/devkit-spec/src/devkit_spec/features/proposals/
    - packages/devkit-spec/src/devkit_spec/features/delivery/
    - packages/devkit-spec/tests/
    - docs/capabilities/delivery/
  excludes:
    - .devkit/managed/
    - packages/devkit-core/
task_kind: feature
decomposed_from: PROP-git-operator-pilot-follow-up
workflow: sdd-proposal
---

# [PROP-git-operator-planning-completion-route] Planning completion and acceptance execution route for git-operator

## 1. Background & Hypothesis

In the resource-indexer consumer pilot (`MAT-git-operator-consumer-pilot`), the Host accepted and integrated a
verified Planning result with `accept --mode accept_only` itself, because the git-operator operating reference lists
handoff and integration but no Planning-acceptance job. A later split route succeeded: the Host recorded and committed
the acceptance, then the operator integrated it. A new job is therefore an option to compare against clearer
guidance for that route, not a prerequisite.

A readiness ambiguity appeared as well. `workflow next` returned no current stage and `complete=yes` under
`plan-accept=auto` while proposals were still `reviewing` and no acceptance command had run. Planning workers needed
Host guidance to record their return at `direction-handoff` instead of the printed `-` sentinel.

This repository's own run on 2026-10-30 also found that `accept --mode` refuses `--check`, so a composed acceptance
cannot be dry-run.

The hypothesis: explicit route guidance and an explicit return stage remove the Host's interpretation at the end of
Planning without widening the operator's role.

## 2. Technical Spike Questions

- **Q1 Acceptance route**: Is explicit guidance for Host acceptance record/commit followed by operator integration
  enough, or does a composed acceptance job reduce measured burden? Either route keeps exact refs, current authority
  and all readiness and permission checks, with no new approval grant or arbitrary Git execution.
- **Q2 Return stage**: Should `workflow next` expose a record/return stage when policy-derived readiness has no current
  stage, or is an explicit worker-guidance mapping enough? `complete=yes` is rendered by
  `packages/devkit/src/devkit_agt/features/workflow/cli/render.py`, outside this boundary: choosing the engine route
  records a boundary extension in Planning. No acceptance is inferred from policy readiness.
- **Q3 Dry run**: Should a composed acceptance offer a read-only check, given that `--mode` refuses `--check`?

## 3. Proposed Design & Impact

- The git-operator contract, spec-orchestrate dispatch and spec-review-proposal document the selected acceptance route.
- Planning worker guidance names the valid stage for a final return under policy-derived readiness.
- `PROP-integration-merge-moved-target` lands first, so this route documents no base-merge step that proposal removes.

Acceptance checks (from the parent's verification candidates):

| ID | Given | When | Then |
| --- | --- | --- | --- |
| GOP-01 | A verified committed Planning source and exact current Host authority | The operator executes Planning acceptance | Only named existing CLI effects run; source drift or missing authority preserves resources and returns the required Host action. |
| GOP-03 | Auto-policy Planning readiness with no current stage and a reviewing proposal | A worker authors its final return | The record uses an explicit valid workflow stage; no acceptance or handoff effect is invented. |
| GOP-06 | A request for production edits, semantic conflict resolution or broader authority | The operator receives the job | It returns that work to the Host or implementer and performs no such mutation. |

### Non-goals

- **Scope Excluded**: a daemon, persistent approval store, global repository lock or autonomous scheduler.
- **Scope Excluded**: operator source authoring, semantic decisions, approval grants, force operations or arbitrary
  remote deletion.
- **Scope Excluded**: changing policy or bypassing a host refusal to make a lifecycle operation succeed.
- **Scope Excluded**: unmeasured token, cost or latency savings.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-git-operator-planning-completion-route`; the proposal is deleted there and its decisions become ADRs.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
