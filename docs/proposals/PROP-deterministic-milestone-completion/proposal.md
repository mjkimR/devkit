---
id: PROP-deterministic-milestone-completion
title: Simple milestone completion from direct proposal checks
summary: "Close milestones from confirmed decomposition and settlement of directly linked proposals, using focused code or Git inspection when needed instead of persistent delivery-lineage tracking."
status: reviewing
created_at: 2026-10-21
target_area: capabilities/delivery/
priority: high
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-spec/
    - docs/capabilities/delivery/
    - docs/capabilities/documents/
    - docs/capabilities/governance/
    - docs/capabilities/harness/
    - docs/decisions/
    - docs/development/reference/
    - docs/roadmap/
  excludes:
    - packages/devkit/src/devkit/integration/
    - packages/devkit-dist/src/devkit/shared/
    - packages/devkit-viewer/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-deterministic-milestone-completion] Simple milestone completion from direct proposal checks

## 1. Background & Hypothesis

Milestones should describe large phases or long-term themes that the user and agent review together and split
into proposals. They should not become a second delivery database. `ADR-milestone-documents` currently requires
separate manual transitions; completing the associated work can leave the milestone planned or active.

The desired closure has two checks: the user and agent have finished decomposing the intended milestone scope
into proposals, and the work represented by its directly connected proposals has been settled. Keep this model
local to the milestone/proposal boundary. Do not carry milestone metadata into SPECs or maintain a persistent
milestone-to-PROP-to-SPEC graph. `PROP-unit-dependencies-and-milestone-scope` owns the direct-membership model and
unit ordering; this proposal owns the small closure procedure built on that boundary.

The agent may inspect relevant code or Git state when deciding whether a removed proposal's work is actually
settled. That is a focused check at the time of review, not a requirement to retain every descendant, branch,
outcome ID or integration record in the milestone. Proposal absence alone remains insufficient: handoff can remove
a proposal before implementation has finished.

## 2. Technical Spike Questions

- **Q1 — Minimal confirmation:** What is the smallest way to record that milestone decomposition is complete and
  that its directly linked proposal work is settled? Prefer two explicit confirmations tied to the current
  milestone scope over per-outcome maps, copied work lists or durable descendant records.
- **Q2 — Direct proposal checks:** How does the review list the milestone's direct proposals and identify ones
  still requiring work? When a proposal has been handed off or removed, what focused code/Git inspection is useful
  before confirming settlement, without propagating milestone metadata to the resulting SPEC?
- **Q3 — Deterministic close:** Once both confirmations hold and no directly linked proposal remains unsettled,
  what existing Backlog command/procedure can set done idempotently? A read-only candidate check must distinguish
  missing confirmation from a failed inspection. Do not add a background evaluator or integration-engine coupling.
- **Q4 — Change handling:** Which direct scope or membership changes invalidate a prior confirmation? Keep that
  rule simple. Rejection, reassignment or deletion requires an explicit disposition, not automatic success from
  the file disappearing. Existing milestones without confirmation remain open until reviewed.

## 3. Proposed Design & Impact

### Collaborative scope, direct ownership

The user and agent review a milestone's high-level goal and create its necessary proposals. Proposal anchors
express direct membership. The milestone does not duplicate their task lists and does not attach its identity to
SPECs. The first closure condition is an explicit confirmation that this decomposition is sufficient for the
agreed scope; merely counting existing proposals cannot establish that no work was omitted.

The second condition is confirmation that directly associated proposal work has been settled. Remaining direct
proposals are reviewed and completed, explicitly removed from scope, or left open. If handoff/removal makes status
unclear, inspect the relevant implementation or Git facts before confirming. Do not treat deletion as proof of
implemented behavior. If the inspection cannot establish settlement, leave the confirmation unset and state the
specific outstanding check.

No persistent outcome-to-unit matrix, transitive lineage index, branch ownership graph or automatically maintained
verification ledger is introduced. Existing PROP/SPEC records remain available for ordinary navigation when useful,
but closure does not require carrying milestone metadata through them or enumerating all historic descendants.

### Small deterministic transition

With decomposition and direct-proposal settlement explicitly confirmed for the current scope, the close operation
can deterministically record done. The tool validates the recorded conditions and current direct membership;
it does not replace the user/agent's judgment about the goal or infer semantic completion from missing files.
Repeated close is a no-op. Done milestones remain historical documents, resolvable by ID and visible with --history;
this is not proposal-style deletion.

A change to the agreed goal or direct membership requires the affected confirmation to be revisited before close.
Cancellation, rejection or moving a proposal is an explicit scope disposition, not delivery success. Activation and
dropping remain user decisions. A PADR should define the narrow policy exception permitting done after prior
confirmation, without relaxing plan-intent, plan-accept or delivery verification.

Prefer checking closure during the existing collaborative Backlog review and after relevant work completes.
Do not make every feature integration maintain milestone state. The exact two-confirmation representation and
supported command are Planning decisions; no new API or schema is fixed by this draft.

### Acceptance evidence

- A milestone with confirmed decomposition and confirmed settlement of its direct proposal work closes once;
  repeat close is harmless and history/ID lookup still works.
- Missing confirmation or an unsettled direct proposal keeps it open and identifies the remaining action.
- A proposal removed by handoff while implementation is unfinished does not justify settlement confirmation;
  a focused code/Git inspection can identify the unfinished work without a stored milestone-to-SPEC relation.
- Explicit cancellation or reassignment updates the reviewed scope; deleting a file alone does not manufacture
  a successful disposition. Scope/membership changes require the affected confirmation to be revisited.
- Milestone metadata is not propagated to SPECs, and no durable descendant/verification graph is required.
  Existing unconfirmed milestones do not auto-close merely because they have no proposals.
- The current user-owned gates remain intact; no background process, generic integration change, automatic
  activation or automatic dropping is introduced.

Use small document/domain fixtures for confirmed/unconfirmed conditions, handoff absence, direct membership
changes and repeat close, plus relevant command/advisory and governance checks. Keep verification proportional
to the chosen small contract; do not build a lineage framework just to test milestone closure.

## 4. Lifecycle & Retirement Criteria

This is a queued feature draft, not approval to start Planning or Development. Planning and Development effort
hints are medium. Planning must settle the minimal confirmation contract and explicitly reject unnecessary
transitive bookkeeping. Keep shared direct-membership semantics aligned with
`PROP-unit-dependencies-and-milestone-scope`; do not implement that proposal's independent unit dependency work here.

**Scope excluded:** automatically guessing all necessary proposals; milestone metadata on SPECs; per-outcome
coverage maps; persistent PROP/SPEC descendant graphs; automatically collected verification/integration ledgers;
closing solely because PROP files are gone; generic integration-engine hooks/refactoring; external trackers;
background monitoring; viewer changes; automatic activation/dropping; mass conversion of the current roadmap.
