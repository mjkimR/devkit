---
id: SPEC-historical-handed-off-references
title: Accept handed-off proposal IDs in work history
summary: Stop RULE-document-reference from reporting a handed-off PROP-<slug> as an unresolved ID in explicitly targeted work history, where handoff never rewrites references, when its SPEC-<slug> exists.
status: planned
created: 2026-10-30
related_capabilities:
  - CAP-GOV-spec-rules
related_usecases:
  - UC-keep-the-living-spec-consistent
workflow: sdd-spec-bugfix
---

# [SPEC-historical-handed-off-references] Accept handed-off proposal IDs in work history

## 1. Problem Statement & Motivation

A spec bundle that completes before a proposal it cites is handed off keeps the `PROP-<slug>` it wrote. Handoff
rewrites live references only, and `CAP-GOV-spec-rules` (section 3.2, History) keeps completed bundles as work history
that a fix never rewrites. Naming such a bundle as an explicit `devkit rules check` target then reports an error that
no fix can clear, so a Host or worker that checks one finished bundle sees a failure the bundle did not cause.

## 2. Defect Characterization

- **Current behavior**: `uv run devkit rules check specs/2026-10/20261030-integration-merge-moved-target` on `main`
  reports two `RULE-document-reference` errors, "no document has the ID PROP-git-operator-planning-completion-route"
  at `reconcile.md` line 80 and `spec.md` line 220, not fixable; the whole-repository `uv run devkit rules check`
  reports none, because history is checked only when targeted. That proposal was handed off to
  `SPEC-git-operator-planning-completion-route` after the bundle completed. In
  `devkit_docs.features.governance.usecases.document_reference` `_reference`, `_handed_off` finds the spec, but the
  `not historical` guard falls through to the generic unresolved-ID error; the unit `depends_on` branch has the same
  shape.
- **Expected behavior and its basis**: the user's `plan-intent` agreement. In work history
  (`DocumentIndex.is_historical`: a completed spec bundle outside its `feedback/`, or a done or dropped milestone) a
  `PROP-<slug>` that no document declares but whose `SPEC-<slug>` resolves to exactly one document is not reported:
  the reference was valid when written and history is never rewritten (`CAP-GOV-spec-rules` section 3.2, History).
  History already resolves alias references silently by the same reasoning (`CAP-GOV-spec-rules` section 3.3).
- **Behavior to preserve**: a current document citing a handed-off `PROP-<slug>` keeps the fixable "was handed off"
  error and its rewrite (`test_brackets_and_handed_off_proposals_are_fixed`,
  `test_late_proposal_reference_is_fixed_to_the_canonical_spec`); a `PROP-<slug>` with no matching spec stays an error
  everywhere, history included; history is still reported only when targeted and never rewritten
  (`test_history_and_materials_are_skipped_unless_targeted`, `test_alias_references_in_history_stay`).
- **Reproduction conditions**: the command above on the base checkout, or a rule test that targets a completed spec
  citing PROP-x in prose and in unit `depends_on` beside a declared SPEC-x.

## 3. Non-Goals

1. **Scope Excluded**: rewriting history, changing the reproduction spec, changing handoff, or treating a
   `PROP-<slug>` without a matching spec as resolved. The bracket and alias findings in history are unchanged.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] A handed-off proposal cited in targeted history is not reported
- **Given** a completed spec bundle that cites PROP-x in prose and lists it in unit `depends_on`, and a declared
  SPEC-x, with no document declaring PROP-x
- **When** `RULE-document-reference` checks with the bundle's `spec.md` as an explicit target
- **Then** it reports 0 violations, a fix leaves the file byte-identical, and
  `uv run devkit rules check specs/2026-10/20261030-integration-merge-moved-target` reports `errors=0`

### [AC-02] A current document keeps the fixable handoff error
- **Given** a current document citing PROP-x beside a declared SPEC-x
- **When** the rule checks it
- **Then** it reports exactly one fixable violation "PROP-x was handed off; reference SPEC-x" (the ID in code-span form)

### [AC-03] An unknown proposal in history stays an error
- **Given** a completed spec bundle citing PROP-gone, with no PROP-gone and no SPEC-gone declared
- **When** the rule checks with the bundle's `spec.md` as an explicit target
- **Then** it reports "no document has the ID PROP-gone", not fixable

## 5. Assumptions

- The unit `depends_on` branch follows the same rule as prose, because the agreed cause names its identical shape: in
  history a handed-off `depends_on` target whose spec is a valid anchor is not reported.
- `CAP-DOCS-document-model` states the canonical mapping and history in general but not handed-off proposal
  resolution, so the contract change belongs to `CAP-GOV-spec-rules` section 3.3 and the rule guide.
