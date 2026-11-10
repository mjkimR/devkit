---
id: PROP-remove-plan-intent-gate
title: Remove the plan-intent gate
summary: "Remove the plan-intent approval gate, its decision records and its guidance from the SDD workflows, because an explicit task instruction already supplies intent and the gate only adds a record, a commit and special cases in acceptance and handoff."
status: draft
created_at: 2026-11-10
target_area: capabilities/delivery/
priority: low
size: L
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/workflows/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/AGENTS.md.jinja
    - packages/devkit-spec/src/devkit_spec/features/proposals/usecases/
    - packages/devkit-spec/src/devkit_spec/features/delivery/
    - packages/devkit-spec/src/devkit_spec/features/policy/
    - packages/devkit-spec/src/devkit_spec/base/errors.py
    - packages/devkit-spec/tests/
    - packages/devkit-docs/tests/integration/bundles/docs/test_distribution.py
    - docs/capabilities/delivery/
    - docs/capabilities/harness/CAP-HARN-agent-guidance.md
    - docs/usecases/delivery/
    - docs/architecture/ARCH-04-delivery-strategy.md
    - docs/architecture/ARCH-04-2-delivery-policy.md
  excludes:
    - specs/
    - packages/devkit/src/devkit_agt/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-remove-plan-intent-gate] Remove the plan-intent gate

## 1. Background & Hypothesis

Every SDD workflow except `sdd-overall-refactor` declares `human_gate: plan-intent` at its intent stage. The default
policy is `ask`, so each proposal pickup and each spec Unit records `decisions/01-gate-plan-intent.yaml` with
`devkit workflow answer` and commits it as its own commit.

The gate settles nothing the conversation has not already settled:

- `ADR-delivery-approval-and-lifecycle-authority` ("Task intent") already treats `plan-intent` as an authorization record, not an
  interruption: "an explicit task instruction already supplies intent". The constitution repeats it ("do not ask for
  the same consent again").
- An agent rule, not the record, keeps the agent from starting unrequested work: "No unrequested task is implicitly
  scheduled" (same ADR).
- The classification the request shows (`size`, `planning_effort`, `task-kind`, `planning-depth`) can be stated in
  the intake reply and corrected at `plan-accept`.
- The `size: XL` block is an exit check of the `intent-proposal` stage
  (`frontmatter(proposal.md size S|M|L|)`), independent of the gate.

The gate still costs:

- one step and one commit per Unit;
- special cases in code: `accept --direct` reports a missing `gate:plan-intent` as pending rather than blocking and
  exempts `plan-intent=auto` (`accept.py`); handoff requires and carries `gate:plan-intent` to the spec
  (`native_handoff.py`, `handoff.py`, `SPEC_PROPOSAL_GATE_NOT_CARRIED`); policy inspection lists the gate;
- guidance in 6 workflows, 11 other spec bundle files, 8 Living Spec documents, the always-loaded `AGENTS.md` block
  and the `spec` skill's start table.

Hypothesis: removing the gate, rather than setting `plan-intent = "auto"`, makes the workflows and their guidance
smaller with no loss of control, because nothing reads the record except the checks that exist to require it.

## 2. Technical Spike Questions

- **Q1**: Where does the depth escalation reason go? `depth-and-close.md` step 3 stores "depth session -> spec:
  <reason>" in the `plan-intent` note. Candidates: `spec.md`, the Unit's first commit message, or no record.
- **Q2**: Does the workflow engine (`devkit_agt`) tolerate the `plan-intent` decision records already committed in
  completed specs and live proposals once no workflow declares the gate? `devkit workflow next` and
  `devkit rules check` must stay clean on them without a migration.
- **Q3**: Do the intent stages keep a reason to exist without a gate (the `intent-proposal` size exit check stays),
  or do some merge into the next stage?
- **Q4**: Does any external consumer need a human confirmation before a task starts? If so, keep it as an opt-in
  policy instead of a default gate; otherwise remove `[workflow.approvals] plan-intent` outright and report a
  configured value as unknown.

## 3. Proposed Design & Impact

- Remove `human_gate: plan-intent` and its `approvals` entry from the 6 SDD workflows and their prose.
- Remove the `plan-intent` steps from the `spec` skill, its references (`backlog`, `depth-and-close`, `classification`,
  `proposals-catalog`, `worktree`, `playbooks`), `spec-next` and `spec-specify` references, and the bundle `AGENTS.md`
  block. The intake reply keeps stating the classification and effort.
- Code: drop the `gate:plan-intent` eligibility condition from `devkit spec proposal accept`, the `plan-intent`
  requirement and carry from `devkit spec proposal handoff`, and `INTENT_GATE` from policy inspection. The approval
  boundaries stay `plan-accept`, `proposal-handoff` and `dev-integration`.
- Living Spec: update `CAP-DLV-proposal-planning`, `CAP-DLV-delivery-workflows`, `CAP-DLV-project-policy`,
  `CAP-HARN-agent-guidance`, the delivery use cases and `ARCH-04-delivery-strategy` and `ARCH-04-2-delivery-policy`.
- Decision: a new ADR superseding in part the "Task intent" outcome and the intent gate of
  `ADR-delivery-approval-and-lifecycle-authority`.

Non-Goals:

- Changing the generic gate mechanism of the workflow engine (`human_gate`, `[workflow.approvals]`, `--given`).
- Rewriting committed `plan-intent` records in completed specs; Git history keeps them.
- Changing `plan-accept`, `proposal-handoff` or `dev-integration`.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` (after Planning, or `--direct` for an eligible draft in
  Backlog); handed off to a spec bundle on `dev-remove-plan-intent-gate`; the proposal is deleted there and its
  decisions become ADRs.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes the
  rejection ADR and deletes the proposal.
