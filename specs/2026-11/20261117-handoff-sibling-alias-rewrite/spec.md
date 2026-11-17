---
id: SPEC-handoff-sibling-alias-rewrite
title: Handoff rewrites alias references to already handed-off proposals
summary: The proposal handoff commit is refused when the carried files cite a sibling proposal that was handed off after this proposal's Planning merged; rewrite such alias references to their current IDs inside the handoff transaction.
status: in-progress
created: 2026-11-17
related_capabilities:
  - CAP-DLV-proposal-lifecycle
related_usecases: []
workflow: sdd-spec-bugfix
---

# [SPEC-handoff-sibling-alias-rewrite] Handoff rewrites alias references to already handed-off proposals

## 1. Problem Statement & Motivation

Two sibling proposals planned in parallel are handed off in sequence. When proposal A's Planning merged before
sibling B was handed off, A's `proposal.md` still cites B by its proposal ID. Once B is handed off, that ID resolves
only through the handed-off `SPEC-` form, so `RULE-document-reference` reports each citation as fixable. The handoff
of A carries the stale citations into its new spec and the composed handoff commit is refused, leaving the
transaction staged and requiring a manual `devkit rules fix` and commit by the Host.

## 2. Defect Characterization

- **Current behavior**: `devkit spec proposal handoff <A> --commit` writes the spec bundle and promoted ADRs, rewrites
  only references to A's own proposal ID, its PADRs and their aliases (`rewrite_ids`), then commits. A carried
  reference to a handed-off sibling proposal ID, or to any other document's alias, stays as written, so the commit
  gate fails with `SPEC_HANDOFF_COMMIT_REFUSED` (`GATE_RULES_FAILED`: "PROP-B was handed off; reference SPEC-B")
  and the writes remain staged. Evidence: `FB-handoff-leaves-stale-sibling-proposal-aliases` (the handoff of
  `SPEC-adr-body-metadata-removal`, three references to the sibling proposal of `SPEC-formal-doc-padding-trim`).
- **Expected behavior and its basis**: `CAP-DLV-proposal-lifecycle` (Host-authorized proposal lifecycle CLI) commits
  the handoff transaction under the normal commit gate, and `ADR-proposal-handoff` gives workers clean committed
  input without an unnamed Host step. The handoff therefore rewrites, in the files it carried and promoted, every
  reference `RULE-document-reference` would fix as an alias (a handed-off `PROP-<slug>` to its `SPEC-<slug>`, and
  an alias of another document to that document's ID) before the commit, reports each as `[REWRITTEN ... kind=id]`,
  and the commit passes.
- **Behavior to preserve**: the handoff's own rename across the whole scan set (`rewrite_ids`), link and path
  rewrites, files outside the carried and promoted set (a sibling draft still in Planning keeps its references), a
  reference to a declared ID, a document's mention of its own alias, bare text and fenced code, and a `depends_on`
  whose replacement would be a problem target. Tests:
  `packages/devkit-spec/tests/integration/features/proposals/test_proposal_aliases.py`,
  `test_proposal_handoff.py`, `test_proposal_handoff_merge.py`, `test_unit_dependencies.py`.
- **Reproduction conditions**: a workspace with an accepted proposal whose body cites a sibling proposal ID that was
  already handed off (its `SPEC-` form exists, no document declares the proposal ID), and an ADR declaring an alias
  that the proposal cites; run `handoff_proposal(root, slug)` and then `RULE-document-reference` on the workspace.

## 3. Non-Goals

1. **Scope Excluded**: rewriting aliases in files the handoff did not write or move (other documents, sibling drafts,
   the base copy of other proposals), in the preserved materials directory, or at plan acceptance; changing
   `RULE-document-reference`, its fixer or the commit gate; converting a non-alias `[ID]` bracket reference.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Carried references to a handed-off sibling proposal are rewritten
- **Given** an accepted proposal whose carried body and PADR cite PROP-sibling, a proposal already handed off to
  SPEC-sibling that no document declares any longer
- **When** the proposal is handed off
- **Then** the carried `spec.md` and the promoted ADR name SPEC-sibling, the result lists one `kind=id` rewrite from
  PROP-sibling to SPEC-sibling per reference, and `RULE-document-reference` reports 0 violations.

### [AC-02] Carried alias references of other documents are rewritten
- **Given** an accepted proposal whose carried body cites ADR-old, an alias another ADR declares
- **When** the proposal is handed off
- **Then** the carried reference names that ADR's ID, the result lists the `kind=id` rewrite and
  `RULE-document-reference` reports 0 violations.

### [AC-03] Files outside the carried set and non-alias references stay
- **Given** a document outside the handoff's written files citing the handed-off sibling ID, a sibling draft still in
  Planning cited by its declared ID, and a carried mention of the new spec's own alias
- **When** the proposal is handed off
- **Then** the outside document is byte-identical, the declared sibling draft ID and the own alias are unchanged in
  the carried files, and the existing handoff alias tests pass unchanged.

## 5. Source feedback

`FB-handoff-leaves-stale-sibling-proposal-aliases`: the handoff rewrites alias references in its carried and promoted
files before the commit.

## 6. Assumptions

- The alias resolution follows `RULE-document-reference` exactly: a handed-off `PROP-<slug>` that no document
  declares maps to the one document `SPEC-<slug>` names, and another document's resolving alias maps to its ID, both
  through `DocumentIndex.canonical`. The short resolution is restated in the proposals feature rather than imported,
  because the rule's helpers are private to `devkit_docs.features.governance`, which is not a declared dependency of
  `devkit_spec.features.proposals`.
- The pass runs after the existing rewrites and only on the files the handoff wrote into the spec bundle (moved
  feedback included) and the promoted ADRs.
- No architectural invariant changes, so no ADR is required.
