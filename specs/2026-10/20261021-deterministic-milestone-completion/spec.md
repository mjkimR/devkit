---
id: SPEC-deterministic-milestone-completion
title: Simple milestone completion from direct proposal checks
summary: Close milestones from confirmed decomposition and settlement of directly linked proposals, using focused code or Git inspection when needed instead of persistent delivery-lineage tracking.
status: completed
created: 2026-10-21
depends_on: [SPEC-unit-dependencies-and-milestone-scope]
related_capabilities: [CAP-DLV-proposal-incubation, CAP-DOCS-document-model, CAP-HARN-agent-guidance]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-deterministic-milestone-completion] Simple milestone completion from direct proposal checks

## 1. Problem Statement & Motivation

Handed off from proposal PROP-deterministic-milestone-completion on 2026-10-21.

### 1. Background & Hypothesis

Milestones should describe large phases or long-term themes that the user and agent review together and split
into proposals. They should not become a second delivery database. `ADR-milestone-documents` currently requires
separate manual transitions; completing the associated work can leave the milestone planned or active.

The desired closure has two checks: the user and agent have finished decomposing the intended milestone scope
into proposals, and the work represented by its directly connected proposals has been settled. Keep this model
local to the milestone/proposal boundary. Do not carry milestone metadata into SPECs or maintain a persistent
milestone-to-PROP-to-SPEC graph. `SPEC-unit-dependencies-and-milestone-scope` owns the direct-membership model and
unit ordering; this proposal owns the small closure procedure built on that boundary.

The agent may inspect relevant code or Git state when deciding whether a removed proposal's work is actually
settled. That is a focused check at the time of review, not a requirement to retain every descendant, branch,
outcome ID or integration record in the milestone. Proposal absence alone remains insufficient: handoff can remove
a proposal before implementation has finished.

## 2. User Stories

As a developer, I want a concrete collaborative milestone close review so that phase completion is explicit without maintaining delivery lineage.

## 3. Non-Goals

**Scope Excluded:** runtime parsers, commands, evaluators, milestone metadata on SPECs, persistent lineage, integration hooks, automatic transitions, viewer changes and migration of existing milestone documents.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Current close decision
- **Given** a planned or active milestone with sufficient decomposition, settled direct work and a met exit condition
- **When** the user confirms both checks on the concrete current candidate
- **Then** the Backlog procedure records Decomposition: confirmed, Direct proposal work: confirmed and status done in one commit without a third approval.

### [AC-02] Missing confirmation or evidence
- **Given** missing assertions/confirmation, unresolved in-scope work, an unmet exit condition or inconclusive required evidence
- **When** closure is reviewed
- **Then** it stays open with the remaining check named; empty membership and handoff absence never certify delivery.

### [AC-03] Explicit scope disposition
- **Given** rejected, cancelled, removed or reassigned proposal work
- **When** the close candidate is prepared
- **Then** exclusion/movement is distinguished from delivery and the resulting agreed scope and exit condition are explicit; unfinished in-scope handed-off work blocks settlement.

### [AC-04] Invalidation and interrupted review
- **Given** an actual semantic scope change (new required work, exclusion or moving scope elsewhere)
- **When** the authorized change occurs
- **Then** both assertions reset to pending in the authorized scope edit; relevant close-time evidence changes require reconfirmation, while unchanged authorization survives pause or compaction. Normal handoff/mechanical identity relocation does not change scope or decomposition and requires no milestone review/reset.

### [AC-05] Historical and terminal milestones
- **Given** a done or dropped milestone
- **When** closure is requested again
- **Then** unchanged done writes nothing and dropped is not a close candidate; done scope extension requires user-owned reopen to active with pending assertions or another milestone, and historical done records are not migrated.

### [AC-06] Shipped guidance and boundaries
- **Given** local and cloud bundle rendering
- **When** guidance and templates are verified
- **Then** both teach the same two-assertion procedure within existing context budgets, without runtime/schema/lineage additions.

## Assumptions

The integrated prerequisite provides direct PROP membership and typed unit ordering. The current predecessor is `ADR-separate-unit-prerequisites-from-milestone-themes`; its unaffected decisions remain in force. Guidance fixtures verify the shipped instructions, not semantic delivery certification.

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Planning Decisions

- **D1 — Existing Backlog operation:** Close through the existing authorized milestone document edit. There is
  no milestone transition command to extend and no demonstrated need to introduce one. Deterministic means the
  procedure has two explicit conditions and a fixed next action; it does not promise automatic semantic validation.
- **D2 — Two body assertions:** Add a `Completion review` section to the milestone template with exactly two
  plain statements: `Decomposition: pending` and `Direct proposal work: pending`. Each becomes `confirmed` only
  after the user confirms the concrete review. These are durable milestone closure assertions, not task checklists,
  frontmatter schema, a verification ledger or a list of work. Existing documents without them are unconfirmed.
- **D3 — Fresh decision:** Prepare both confirmations for the current scope together with the close candidate.
  The user's confirmation of both authorizes the existing `status: done` edit; no separate third approval is needed.
  Record both `confirmed` statements and `done` in the same Backlog commit. Stored body assertions alone never authorize a later close. After a pause, re-establish the approved
  candidate and recheck scope, membership and relevant evidence; unchanged authorization remains valid. Reconfirm
  only when material facts changed or the approved candidate and its evidence cannot be established.
- **D4 — Direct work only:** Review all current direct PROP members and relevant known activity, using ordinary
  document queries and focused code/Git inspection. No SPEC receives milestone metadata. Handoff, deletion,
  rejection and reassignment alone are not evidence of delivery. An unresolved proposal still in scope blocks
  settlement, regardless of draft/reviewing/accepted status. Explicitly excluded or moved work is settled only as a
  scope disposition, never reported as implemented. Remaining rejected anchors likewise require an explicit
  disposition. Do not reconstruct or persist a complete descendant graph.
- **D5 — Reconfirmation:** Actual semantic scope changes (new required work, exclusion or moving scope elsewhere) clear
  both assertions to `pending` in the authorized scope edit. Normal handoff/mechanical identity relocation does not
  change scope or decomposition and requires no milestone review/reset. Removal still does not prove completion. Pure wording/format corrections that preserve meaning do not invalidate.
  To extend a done milestone's scope, first obtain the user's decision to reopen it as `active` and reset both
  assertions in the scope edit; alternatively put the new scope in another milestone. No automatic reopening.
- **D6 — Keep authority and scope small:** Activation and dropping remain the user's decisions. Closure works
  from planned or active after the review; a current done milestone is a no-op unless its scope is being reopened.
  Dropped milestones are not close candidates. No background evaluator, new command, new parser field, hash,
  approval envelope, branch ledger or integration hook is introduced. Existing done milestones remain historical
  and are not retroactively reopened or migrated.

`ADR-milestone-closure-confirmations` records the representation and policy choice. Development starts only after
`SPEC-unit-dependencies-and-milestone-scope` integrates; that work owns direct PROP membership and unit ordering.
Planning does not add an unsupported dependency field before that work is available.

### 3. Proposed Design & Impact

#### Collaborative close procedure

1. Read the milestone's goal, exit condition and non-goals. The user and agent review whether the required work
   has been decomposed sufficiently into proposals. The first confirmation asserts no intended scope remains
   undecomposed; a zero-member count cannot establish it.
2. Inspect direct PROP membership across namespaces using existing list/refs queries, distinguishing membership
   from ordinary prose references. Check the selected local base and relevant known Planning/Development activity
   without switching another task's checkout. Report the base commit used, without implying remote freshness.
   When work disappeared through handoff or another lifecycle action, inspect the focused code/Git facts needed
   to establish its disposition and the milestone's phase-level exit outcome. Do not enumerate every historic
   descendant or require a saved MS-to-PROP-to-SPEC mapping.
3. Present one concrete close candidate: decomposition sufficient, directly associated work delivered or explicitly
   excluded/moved, and exit condition met for the resulting agreed scope. Explicit scope reduction updates the goal
   or exit condition where needed. State delivery and exclusion distinctly. Known outstanding work or a missing,
   unreadable or inconclusive required inspection keeps the milestone open and names the remaining check. Missing
   user confirmation is reported separately from an evidence gap; an empty query alone establishes neither check.
4. Obtain the user's two confirmations together and record the body assertions plus `status: done` in the same
   Backlog edit/commit. Re-read current scope and membership immediately before writing; a changed candidate is
   presented again. Do not reuse approval of a stale candidate. After interruption, recheck the approved candidate and relevant facts; preserve authorization when unchanged.
   Reconfirm only after a material change or when the prior candidate/evidence cannot be established. A pause or
   context compaction alone does not require another user decision. Report the resulting status. A repeat against an unchanged done document writes nothing.

The agent applies these steps during requested collaborative Backlog review and can propose the review after known
associated work finishes. It does not silently mutate milestones after every integration. User/agent reasoning is
the semantic check; ordinary governance rules still validate document shape and references. No rule claims to prove
that two words certify delivery. Existing hygiene continues to identify direct unsettled members on finished
milestones under the prerequisite proposal's semantics.

#### Change placement

- Source bundle milestone template, Backlog guidance and `spec-next` guidance: teach the two assertions, fresh
  close review, explicit dispositions, invalidation and no-op behavior. Any Backlog lifecycle/membership edit that
  changes scope resets the assertions in the same authorized change; normal handoff needs no milestone edit.
- Source seeded roadmap README and repository roadmap README: describe the short collaborative review and direct
  PROP ownership; do not edit individual roadmap milestones.
- `CAP-HARN-agent-guidance`, `CAP-DOCS-document-model`, `CAP-DLV-proposal-incubation` and their directly affected
  quick references: reconcile the procedural/body contract. Keep document parsing and membership services unchanged.
- Promote the PADR as the follow-on to the prerequisite's milestone decision: replace its closure/branch-enumeration
  policy with focused review, retain its direct PROP membership and unit ordering decisions, and preserve user-owned
  transitions. Resolve the actual predecessor ADR after prerequisite integration; do not supersede an older ADR
  in a way that loses the intervening decisions. No exception delegating done to an automatic tool is needed.

#### Acceptance evidence

- A planned or active milestone with sufficient decomposition, settled direct work and a met exit condition is
  shown to the user; both fresh confirmations produce `confirmed` body assertions and done in one commit.
- Missing confirmation, a remaining in-scope PROP, unmet exit condition or inconclusive required evidence keeps
  the milestone open with a specific next action. Empty membership and handoff absence alone do not close it.
- Explicit rejection/cancellation/reassignment is a scope decision, with any reduced exit condition made explicit;
  it is never described as delivery. An unfinished handed-off implementation blocks settlement when still in scope.
- Changing the actual phase-level scope invalidates both confirmations; mechanical handoff does not.
  A handoff alone neither authorizes close nor invalidates an unchanged approved candidate. A materially changed close candidate is re-presented; an interrupted review
  resumes under existing authorization when its candidate and evidence are established unchanged. Reopening a done milestone requires the user's scope decision; harmless formatting does not reopen it.
- A repeat close against an unchanged done milestone is a no-op. Old done records are retained without migration;
  old open records without assertions need review. Dropped records are not silently changed to done.
- No SPEC milestone metadata, persistent delivery graph, new completion API/schema or integration coupling is added.

Use focused bundle contract tests for the shipped template/instructions and representative procedure fixtures for
fresh/missing confirmations, unfinished handoff, explicit exclusion, changed scope, interrupted review with unchanged versus changed facts and repeated
close. Reuse existing milestone history/lookup tests; no new semantic evaluator is built for testing. Development
runs lint, types, relevant affected tests and governance checks. Development effort remains medium because this
changes a lasting closure policy and its shipped guidance, even though no runtime service is added.

### 4. Lifecycle & Retirement Criteria

Planning is ready for the user's direction decision after independent Scout and Challenger review. Development
waits for the direct-membership prerequisite to integrate and reconciles its actual resulting contracts before
implementation. This proposal does not approve or perform current milestone closure.

**Scope excluded:** automatic decomposition; milestone metadata on SPECs; per-outcome coverage maps; persistent
PROP/SPEC lineage; branch ownership and verification ledgers; closing because files disappear; generic integration
changes; external trackers; background monitoring; viewer changes; automatic activation/dropping/reopening; mass
conversion of existing roadmap documents; a completion command or machine-certified delivery evaluator.

