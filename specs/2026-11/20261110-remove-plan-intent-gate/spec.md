---
id: SPEC-remove-plan-intent-gate
title: Remove the plan-intent gate
summary: Remove the plan-intent approval gate, its decision records and its guidance from the SDD workflows, because an explicit task instruction already supplies intent and the gate only adds a record, a commit and special cases in acceptance and handoff.
status: planned
created: 2026-11-10
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-remove-plan-intent-gate] Remove the plan-intent gate

## 1. Problem Statement & Motivation

Handed off from proposal PROP-remove-plan-intent-gate on 2026-11-10.
- **Preserved Materials**: `docs/materials/2026-11/20261110-remove-plan-intent-gate`

### 1. Background & Hypothesis

All six SDD workflows, including `sdd-overall-refactor`, declare `human_gate: plan-intent` at its intent stage. The default
policy is `ask`, so each proposal pickup and each spec Unit records historical Git `a74c84afc72b193f32131242b223b76539500ba0:docs/proposals/PROP-remove-plan-intent-gate/decisions/01-gate-plan-intent.yaml` with
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

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Remove the plan-intent gate so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Technical Spike Findings

Evidence is pinned to source `4a6223361b6a60171be665db598b4a81b277d38f`; details are in
`docs/materials/2026-11/20261110-remove-plan-intent-gate/planning-evidence.md`.

- **Q1 Depth escalation**: record the reason, agreed intent and retained work in `spec.md` under a classification
  note. Do not replace the removed approval record with another record or a special commit requirement.
- **Q2 Historical records**: retain valid existing decision files in live and completed Units. The generic loader
  validates request shape, not membership in the current gate list. Development verifies both `workflow next` and
  rules on a Unit containing an old record after removing the workflow gate. Handoff stops selecting and carrying
  `gate:plan-intent`; proposal retirement keeps its ordinary record-drop behavior and Git history.
- **Q3 Intent stages**: retain `intent`, `intent-proposal`, `intent-session` and `intent-refactor` IDs, entry/exit
  checks and return targets. Set their human gate to false, rename their display name to task scope or proposal
  eligibility, and keep the proposal size check. Removing stage IDs risks historical envelopes and adds no value
  to removing the gate.
- **Q4 Configuration**: remove the built-in policy entry. A configured `plan-intent` is a retired SDD key: omit it
  from active policy output, warn with the existing `SPEC_APPROVAL_KEY_IGNORED` notice and instruct removal. Preserve
  generic custom workflow gates and their engine configuration semantics. No opt-in SDD intent gate remains.

### 3. Proposed Design & Impact

- Set `human_gate: false` and remove `gates.plan-intent` from all six SDD workflows, including
  `sdd-overall-refactor`. Remove gate prose while retaining intent stage IDs and their non-gate checks.
- Remove the `plan-intent` steps from the `spec` skill, its references (`backlog`, `depth-and-close`, `classification`,
  `proposals-catalog`, `worktree`, `playbooks`), `spec-next` and `spec-specify` references, and the bundle `AGENTS.md`
  block. The intake reply keeps stating the classification and effort.
- Code: drop the `gate:plan-intent` eligibility condition from `devkit spec proposal accept`, the `plan-intent`
  requirement and carry from `devkit spec proposal handoff`, and `INTENT_GATE` from policy inspection. The approval
  boundaries stay `plan-accept`, `proposal-handoff` and `dev-integration`. Keep `gate:plan-accept` carry and its
  existing warning behavior; narrow `SPEC_PROPOSAL_GATE_NOT_CARRIED` wording rather than removing the code.
- Living Spec: update `CAP-DLV-proposal-planning`, `CAP-DLV-delivery-workflows`, `CAP-DLV-project-policy`,
  `CAP-HARN-agent-guidance`, the delivery use cases and `ARCH-04-delivery-strategy` and `ARCH-04-2-delivery-policy`.
- Decision: a new ADR superseding in part the "Task intent" outcome and the intent gate of
  `ADR-delivery-approval-and-lifecycle-authority`. The earlier ADR remains accepted; unrelated authority clauses
  stay in force. The PADR also names affected clauses in `ADR-proposal-acceptance`, `ADR-delivery-classification`,
  `ADR-roadmap-and-milestones-ledger` and `ADR-ux-screens`; reconciliation adds partial pointers to each without
  changing unrelated decisions or accepted status. UX alternatives remain settled before implementation.
  Reconcile the four declared English handbook pages with the same behavior.

#### Planning decisions

- Remove the gate rather than default it to `auto`: `auto` retains its declarations, policy handling and handoff
  special cases. Keeping the existing gate retains duplicate bookkeeping. The durable choice is recorded in
  `ADR-remove-plan-intent-gate`.
- Task authorization remains an explicit instruction. Backlog items are never implicitly scheduled; goal, scope,
  expected bugfix behavior and classification remain stated before work begins. No replacement approval is added.
- Development remains one feature spec at `medium` effort. It changes one lifecycle rule across its adapters, assets
  and contracts; it does not require a second spec or a new feature dependency.
- Bundle synchronization outputs are admitted only through the existing sync-output class; generated files are
  regenerated, never hand-edited. Historical specs, materials and archived documents are not rewritten.

#### Acceptance and verification

1. All six deployed workflows validate without declaring or requesting `plan-intent`; proposal `size: XL` still
   blocks eligibility. Other gate policies and bugfix Red/Green stages retain their behavior.
2. Direct acceptance and composed handoff work without an intent record. Handoff carries only the existing
   acceptance audit record, and a missing `plan-accept` still refuses. Test ask and auto policy paths.
3. Valid old intent decisions remain unchanged and do not make `workflow next` or rules fail in live/completed
   Units. Historical intent-stage envelopes and return targets remain valid.
4. Policy output contains the three boundaries and configured custom gates, with no default intent entry.
   A retained `plan-intent = "ask"`, `"auto"` or `"off"` emits the ignored-key warning and no active intent entry.
5. Depth escalation records its reason in `spec.md`. Source skills, deployed guidance, capabilities, use cases,
   architecture and English handbook pages describe the same authorization boundary.
6. Run bundle sync, required lint/types/rules and `just test-affected` with full fallback; run selected native E2E
   synchronously in Development. Verify distribution and handoff/policy/size regressions. No timing gain is claimed.

Non-Goals:

- Changing the generic gate mechanism of the workflow engine (`human_gate`, `[workflow.approvals]`, `--given`).
- Rewriting committed `plan-intent` records in completed specs; Git history keeps them.
- Changing `plan-accept`, `proposal-handoff` or `dev-integration`.

### 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` (after Planning, or `--direct` for an eligible draft in
  Backlog); handed off to a spec bundle on `dev-remove-plan-intent-gate`; the proposal is deleted there and its
  decisions become ADRs.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes the
  rejection ADR and deletes the proposal.

