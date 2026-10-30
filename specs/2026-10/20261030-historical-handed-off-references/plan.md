---
id: PLAN-historical-handed-off-references
spec: SPEC-historical-handed-off-references
---

# Technical Plan: `SPEC-historical-handed-off-references` Accept handed-off proposal IDs in work history

## 1. Constitution & Invariant Review

None. The change narrows one finding of `RULE-document-reference` to the history rule `CAP-GOV-spec-rules` already
states (section 3.2, History: checked only when targeted, never rewritten) and to the agreed expected behavior of
`SPEC-historical-handed-off-references`. History already resolves alias references silently for the same reason
(section 3.3), so no architecture invariant or accepted ADR changes. No ADR is needed.

## 2. Architecture Overview & Impact

- `packages/devkit-docs/src/devkit_docs/features/governance/usecases/document_reference.py`,
  `DocumentReferenceRule._reference`: when `_handed_off` finds the canonical spec of an undeclared `PROP-<slug>`, a
  historical document returns without a violation, and a current document keeps the fixable "was handed off"
  violation. The unit `depends_on` branch does the same when the replacement passes `target_problem`; a replacement
  that is not a valid anchor keeps the existing error. A `PROP-<slug>` with no spec keeps the generic unresolved-ID
  error everywhere. `fix` already skips historical documents and is unchanged. The module docstring states the new
  behavior.
- The rule guide (`packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/document_reference/guide.md`) and
  `CAP-GOV-spec-rules` section 3.3 state that a handed-off proposal resolves silently in history. Editing the guide, a
  bundle source the project selects, requires `uv run devkit sync`, which updates `.devkit/installation.json`.
- `CAP-DOCS-document-model` states no handed-off proposal resolution, so it is unchanged.

## 5. Error Handling & Edge Cases

- A historical document whose PROP has a spec through an alias: `_handed_off` already returns the canonical ID of the
  aliased spec, so it is accepted like a declared one.
- A historical document targeting a PROP whose slug matches several specs: `index.canonical` returns `None`, so
  `_handed_off` returns `None` and the ambiguity stays an error.

## 6. Verification & Test Plan

- Regression tests in `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/document_reference/tests/test_rule.py`:
  a targeted completed spec citing a handed-off PROP in prose and in `depends_on` reports nothing and is never
  rewritten (AC-01); a current document keeps the fixable error (AC-02, also held by the existing
  `test_late_proposal_reference_is_fixed_to_the_canonical_spec`); a targeted completed spec citing an unknown PROP
  keeps the unresolved-ID error (AC-03).
- `just test devkit-docs <rule test path>`, `just lint devkit-docs`, `just check devkit-docs`, `just test-affected`
  (with its `mode=full` fallback), `uv run devkit sync --check`, `just rules-check`, and the reproduction command
  `uv run devkit rules check specs/2026-10/20261030-integration-merge-moved-target`.
