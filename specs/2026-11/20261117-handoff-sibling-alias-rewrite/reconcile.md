---
reconcile_id: REC-handoff-sibling-alias-rewrite
status: pending
targets:
  - file: docs/capabilities/delivery/CAP-DLV-proposal-lifecycle.md
    resolution: modified
  - file: docs/designs/delivery/DESIGN-proposal-handoff/design.md
    resolution: modified
related_designs:
  - DESIGN-proposal-handoff
formal_docs:
  domain: "none: no delivery term or relationship changes; the pass only rewrites references inside carried documents"
  operations: "none: no command, configuration or operational procedure changes; the handoff CLI and its codes keep their interface"
---

# Reconciliation: `SPEC-handoff-sibling-alias-rewrite`

## Contract comparison

`CAP-DLV-proposal-lifecycle` §4.1 step 6 and §4.3 now state that, after the existing rewrite passes, the handoff
rewrites in the carried spec bundle files (moved feedback included) and the promoted ADRs every reference
`RULE-document-reference` fixes as an alias: a handed-off `PROP-<slug>` that no document declares to the one
document `SPEC-<slug>` resolves to, and another document's resolving alias to its ID. The implementation
(`rewrite_aliases` and `current_id` in the proposals rewrite service, called last by `handoff_proposal`) applies
exactly that resolution through `DocumentIndex.canonical`, rewrites with the shared reference writer the rule's fixer
uses, skips the `proposal` provenance field, a document's own alias and a unit anchor's `depends_on` whose
replacement has a target problem, and reports each change as `kind=id`. The §4.8 row of
`SPEC_PROPOSAL_REFS_REWRITTEN` and the notice message now cover these rewrites; the code, severity and output
format are unchanged. `DESIGN-proposal-handoff` §4 lists the fifth pass and its update trigger.

`UC-plan-and-hand-off-a-proposal` scenario 3 still holds as written (references into the proposal follow it), so it
is unaffected. `CAP-DLV-proposal-planning` cites the notice by code only and is unaffected. The `spec-next`
post-handoff guidance follows every `[REWRITTEN ... kind=id]` line by code and needs no change. No CLI flag, JSON
field, error code, architecture edge or dependency changes.

## Source feedback

`FB-handoff-leaves-stale-sibling-proposal-aliases` is directly addressed: the regression tests in
`test_proposal_aliases.py` reproduce the stale sibling and alias references (Red at the reproduce stage) and pass
with the fix, and `RULE-document-reference` reports no violation on the carried files after the handoff. The item is
resolved with its evidence.

## Verification scope

The change stays in `devkit_spec.features.proposals` and its own capability and design; it reuses
`devkit_docs.features.documents`, an already declared edge.

## Entrypoints

`devkit spec entrypoints derive` proposed `rewrite.py` and the alias tests for `CAP-DLV-proposal-lifecycle` and the
tests for `DESIGN-proposal-handoff`. All were rejected: the capability already declares its doorway `handoff.py`,
`rewrite.py` is a helper, tests are no doorways, and the design already declares both changed source files.
