---
id: PROP-deterministic-milestone-completion
title: Deterministic milestone completion from confirmed scope
summary: "Confirm complete milestone outcome coverage and derive automatic completion from verified, integrated delivery lineage rather than proposal deletion."
status: draft
created_at: 2026-10-21
target_area: capabilities/delivery/
priority: high
size: L
planning_effort: high
dev_effort: high
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

# [PROP-deterministic-milestone-completion] Deterministic milestone completion from confirmed scope

## 1. Background & Hypothesis

`ADR-milestone-documents` makes milestone transitions explicit user decisions. Units declare membership, while
Backlog separately checks exit conditions and unsettled work before closing. Hygiene warns when a finished
milestone retains unsettled base members, but does not identify a close candidate. Consequently, completing and
integrating all intended work can leave a milestone planned or active until a separate review occurs.

A deterministic close needs two facts: the intended scope is fully represented, and every required outcome has
verified settlement. The absence of proposals proves neither. Handoff removes a proposal when Development starts;
plain deletion, rejection or reassignment does not prove delivery. Counting only extant members also misses work
that has not yet been created or has lost its linkage.

The hypothesis is that user-confirmed outcome coverage can provide a finite completion contract. Once that
contract is fixed, tools can evaluate delivery lineage and automatically record done when every condition holds.
Human judgment establishes scope and verifies the work through existing gates; the completion evaluator consumes
that evidence rather than deciding semantic adequacy or granting new authority.

## 2. Technical Spike Questions

- **Q1 — Scope commitment:** What minimal durable representation names required outcomes, their PROP/SPEC owners,
  and explicit confirmation that decomposition is complete? How does it bind approval to an exact scope revision
  without duplicating tasks or maintaining a second work list?
- **Q2 — Lineage and settlement:** Which existing handoff, decomposition and supersession records can preserve
  outcome ownership after proposal removal? What additional durable evidence is necessary for deleted anchors,
  direct spec intake, split/combined work and source records retained only in Git?
- **Q3 — Evidence authority:** How should the evaluator establish completed tasks, required verification,
  reconciliation and base integration without treating a status flag or proposal absence as sufficient? Define
  exact branch/ref inspection coverage and an unknown result when required evidence cannot be inspected.
- **Q4 — Trigger and atomicity:** Where should read-only evaluation and the authorized done transition run after
  integration and Backlog changes? Prefer an existing devkit-spec extension boundary; determine transaction,
  recheck, retry and recovery semantics without modifying the generic integration package unnecessarily.
- **Q5 — Scope changes and existing milestones:** Which changes invalidate the scope commitment and require
  reconfirmation? Existing planned/active milestones without commitment must remain unconfirmed, not auto-close.
  Determine behavior for newly discovered work after done, stale evidence and direct manual status edits.

## 3. Proposed Design & Impact

### Two independent completion conditions

1. **Confirmed coverage:** Each required milestone outcome has an explicit delivery owner or an authorized scope
   exclusion, and the user has confirmed that decomposition covers the complete intended scope. Merely creating
   some proposals or observing zero members does not establish completeness. Unrepresented requirements prevent
   commitment. A deliberately empty scope requires an explicit disposition rather than vacuous completion.
2. **Verified settlement:** Each included outcome resolves through its delivery lineage to work that is completed,
   has the required verification and resolved reconciliation evidence, and is integrated into the selected base.
   Related active Planning/Development branches must not contain unsettled work. An already-integrated leftover
   branch is a cleanup observation, not an unfinished deliverable. Missing or ambiguous evidence means unknown,
   never done; unavailable required branch evidence prevents a settlement claim.

A milestone becomes eligible only when both conditions hold against the same current scope and repository state.
The automatic transition writes status done with inspectable evidence and is idempotent. It does not delete the
milestone: done/dropped history, ID resolution and dependent milestone readiness retain their existing meaning.

### Deletion, cancellation and scope revisions

Proposal handoff transfers ownership to the SPEC; it never settles the outcome by itself. Decomposition must
preserve coverage across child proposals, and supersession must identify the successor rather than silently lose
the requirement. Rejection, deletion, abandonment or moving a unit to another milestone does not count as
completion. Excluding a required outcome needs an explicit user decision and an updated scope commitment. Retain
the reason and provenance. A completed outcome can be delivered by multiple units, and one unit can serve several
outcomes; Planning must avoid making unit counts the completion model.

Changes to required outcomes or their ownership after commitment invalidate the prior completion decision input.
Do not silently reuse approval for a larger or reduced scope. Activation, dropping and unrelated user-owned
plan-intent/plan-accept gates remain unchanged. The selected policy exception is specifically automatic done under
a previously confirmed completion contract; a PADR/ADR must replace the relevant all-transitions-manual rule.

### Integration with delivery

Expose deterministic read-only completion evaluation that names each satisfied, unmet or unknown condition and
its stable code/evidence. Connect evaluation to the appropriate successful integration/Backlog lifecycle point so
completed work does not rely on a separate conversational reminder. Re-evaluate changed inputs before writing;
concurrent new membership or scope changes must not produce a stale done transition. Repeated evaluation and
resumed cleanup must not create duplicate decisions or commits. A failed milestone update must report remaining
work distinctly from the already-completed feature integration.

Keep the machinery in devkit-spec when existing extension contracts suffice. Do not add scheduling, background
agents or external trackers. The design must preserve branch isolation and permissions; read-only inspection
never mutates Git. Exact command names, stored fields and the mutation boundary are Planning decisions rather
than APIs invented by this draft.

### Expected acceptance evidence

- Confirmed complete coverage plus all verified, integrated owners produces done once and keeps the historical
  milestone resolvable; default discovery hides it and dependent readiness reflects it.
- Unconfirmed/incomplete coverage, no members, missing owners, malformed lineage or unknown branch evidence does
  not close. Results identify the unmet condition rather than reporting generic success.
- Handoff removes the PROP while the SPEC is unfinished: the milestone remains open. Completed but unintegrated
  work, open problems/questions, unresolved reconciliation or missing required verification also remains open.
- Split, superseded, rejected, deleted and reassigned proposals preserve requirements or require explicit scope
  exclusion/reconfirmation; deletion alone never satisfies an outcome.
- A scope or relevant ref changes between evaluation and transition: the stale result cannot close the milestone.
  Retry/recovery is bounded and idempotent; delivery success and milestone-update failure remain distinguishable.
- Existing unconfirmed milestones do not auto-close. Other gates and manual drop/activation authority remain intact;
  completed milestone history is not pruned as if it were a proposal.

Verification should cover domain fixtures for each lifecycle, real isolated Git branch/handoff/integration cases,
CLI output/advisory contracts, targeted rules and relevant lint/types plus just test-affected. Planning must define
what evidence is sufficient and what is intentionally unknown; implementation cannot infer missing evidence.

## 4. Lifecycle & Retirement Criteria

This is a queued feature proposal, not an accepted policy change or authorization to run Planning/Development.
Planning and Development effort hints are high because the change introduces a completion contract, provenance
rules and an automatic lifecycle mutation across several existing boundaries. Do not auto-assign this draft to
an existing milestone whose confirmed scope would be affected by the design under discussion.

Planning must compare a minimal confirmed-coverage representation with alternatives, audit existing provenance
and integration hooks, and produce a verifiable design plus a PADR for the user-owned-transition policy change.
The accepted design must account for every exception above without duplicating unit task lists. Reconcile the
current document, workflow, hygiene and agent-guidance contracts when implementation is separately authorized.

**Scope excluded:** automatically guessing all necessary work; using deleted PROP counts as delivery evidence;
new semantic quality judgments outside existing verification; weakening approval gates; automatic milestone
activation or dropping; external issue trackers; background monitoring; viewer work; generic integration-engine
refactoring; mass acceptance or completion of existing milestones.
