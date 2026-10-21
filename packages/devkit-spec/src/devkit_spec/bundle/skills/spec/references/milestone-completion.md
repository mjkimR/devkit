# Milestone completion review

Read for a requested Backlog close review, or when proposing one after known associated work finishes.
This is a user/agent semantic review, not an automatic evaluator or an integration hook.

## Prepare one current candidate

1. Read the goal, exit condition and non-goals. Review whether all intended scope has been sufficiently
   decomposed into proposals. Empty membership alone establishes neither decomposition nor settlement.
2. Use `devkit spec list proposal --all-namespaces -n 0` and
   `devkit spec refs MS-<slug> --direction in -n 0` to inspect all current direct PROP members across namespaces;
   distinguish frontmatter membership from ordinary prose references. Inspect the selected local base and
   relevant known Planning/Development activity, without switching another task's checkout. Report the base
   commit used; do not imply remote freshness. Use focused code/Git inspection when a proposal disappeared
   through handoff or another lifecycle action. Do not reconstruct or persist a complete descendant graph.
3. Prepare one concrete candidate: sufficient decomposition, directly associated work delivered or explicitly
   excluded/moved, and the phase-level exit condition met for the resulting agreed scope. Distinguish delivery
   from exclusion or movement; update the goal/exit condition when scope reduction requires it.
   An unresolved in-scope proposal blocks settlement whether draft, reviewing or accepted. A retained rejected
   anchor requires an explicit scope disposition. Handoff, deletion, rejection and reassignment alone never
   prove delivery; unfinished handed-off work still in scope blocks settlement.
4. Keep the milestone open for outstanding work, an unmet exit condition or missing/unreadable/inconclusive
   required evidence, naming the remaining check. Report missing user confirmation separately from evidence gaps.

## Confirm and write

The milestone body has exactly two plain assertions under `Completion review`:

Decomposition: pending
Direct proposal work: pending

Missing assertions on an existing open milestone mean unconfirmed. Stored confirmed assertions alone never
authorize a later close. Present both confirmations together with the concrete candidate. The user's confirmation
of both authorizes recording `Decomposition: confirmed`, `Direct proposal work: confirmed` and `status: done`
in the same Backlog edit/commit; no third approval is needed. Closure is available from planned or active.

Immediately before writing, re-read current scope and direct membership and recheck relevant evidence. If semantic scope or relevant completion
evidence changed, present the changed candidate again for confirmation. After pause or context compaction, establish
the approved candidate and recheck those facts; unchanged authorization persists. Reconfirm only when semantic scope or relevant completion
evidence changed or the approved candidate/evidence cannot be established. Interruption alone does not invalidate.

## Changes and terminal records

Actual semantic scope changes, such as new required work, exclusion or moving scope elsewhere, reset both
assertions to pending in the authorized scope edit. Normal PROP-to-SPEC handoff or mechanical identity relocation
does not change scope/decomposition and requires no milestone review, reset or reconfirmation. Handoff still
proves no delivery: check relevant completion evidence at close. Pure wording/format corrections preserving
meaning do not invalidate. No pre-handoff or integration hook is needed.
To extend done scope, first obtain the user's decision to reopen to active and reset both assertions in the scope
edit, or put the new scope in another milestone. Activation and dropping remain user-owned decisions.
An unchanged done milestone is a no-op: write nothing. Dropped milestones are not close candidates. Existing done
records remain historical without migration or retrospective reopening. No SPEC milestone metadata, schema field,
command, approval envelope, branch ledger or stored delivery lineage is introduced.
