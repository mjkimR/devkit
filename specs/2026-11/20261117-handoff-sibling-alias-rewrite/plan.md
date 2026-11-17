---
id: PLAN-handoff-sibling-alias-rewrite
spec: SPEC-handoff-sibling-alias-rewrite
---

# Technical Plan: `SPEC-handoff-sibling-alias-rewrite`

## 1. Constitution & Invariant Review

Keep `ARCH-05-2-components` ownership: the change stays in the `devkit_spec.features.proposals` rewrite service and
the handoff use case, with no new feature edge (`devkit_docs.features.documents` is already declared). The handoff
transaction order and roll-back of `DESIGN-proposal-handoff` stay; the new pass runs in the no-raise rewrite phase.
No ADR is required.

## 2. Architecture Overview & Impact

Add `rewrite_aliases` to `services/rewrite.py`: for each carried or promoted file it parses the document, maps every
reference that `RULE-document-reference` treats as a fixable alias to the current ID, rewrites it with
`devkit_docs.features.documents.services.rewrite.rewrite` (the same writer the rule's fixer uses) and reports each
change as a `kind=id` `Rewritten`. The mapping mirrors the rule: a `PROP-<slug>` no document declares maps to the one
document `SPEC-<slug>` names (`DocumentIndex.canonical`); otherwise a target that `DocumentIndex.canonical` resolves
through an alias of another document maps to that document's ID; a unit anchor's `depends_on` is skipped when the
replacement has a `target_problem`. Historical documents are never in the set.

`handoff_proposal` runs it last, after `rewrite_paths`, on the Markdown files under the new spec directory and the
promoted ADR paths, with the index loaded after the writes. The `SPEC_PROPOSAL_REFS_REWRITTEN` notice keeps its code
and now describes rewritten references generally.

Alternatives: importing the rule's private helpers would need a new `devkit_spec.features.proposals` to
`devkit_docs.features.governance` edge and couple to private names; running the whole rules fixer inside the handoff
would touch files outside the transaction and depend on project rule configuration. Both are rejected.

## 6. Verification & Test Plan

Add Red-then-Green integration tests to `test_proposal_aliases.py` for AC-01 to AC-03 that run the handoff and then
`RULE-document-reference`. Run the proposals integration tests, `just lint-check`, `devkit rules check --ci --base
main` and `just test-affected --base main`. Update `CAP-DLV-proposal-lifecycle` §4.1 and §4.3 and the
`DESIGN-proposal-handoff` rewrite passes, then resolve `FB-handoff-leaves-stale-sibling-proposal-aliases`.
