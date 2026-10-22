# Ledger and index evidence (Planning, 2026-10-22)

Gathered by the planning worker at base `fd6f011b` to ground the direction review.

## ADR ledger size and supersession

- `docs/decisions/2026-10/` holds 74 ADRs: 67 `accepted`, 7 `superseded`.
- Longest supersession chains are three records:
  - approval-gates-intent-direction-integration -> integration-approval-asserted -> policy-authorized-local-integration
  - milestone-documents -> separate-unit-prerequisites-from-milestone-themes -> milestone-closure-confirmations
- Supersede metadata has drifted: `ADR-integration-approval-asserted` and `ADR-milestone-documents` are superseded by
  a later ADR's `supersedes` field but still say `status: accepted` with no `superseded_by`.
- References to superseded ADRs (Markdown under `docs/`, `specs/`, `packages/`; outside `docs/decisions/` in
  parentheses): handoff-workflow-key 3 (3), dist-module-split 27 (20), worktree-and-pull-request-levels 13 (7),
  approval-gates-intent-direction-integration 6 (6), scope-maintenance-through-skills 7 (7),
  medium-review-delegation 12 (6), feedback-resolution-lifecycle 5 (3). The still-`accepted` but superseded
  `ADR-integration-approval-asserted` is mentioned 38 times.

## Index and rule behaviour today

- `DocumentIndex` (`packages/devkit-spec/src/devkit_spec/features/documents/repositories/index.py`) keeps `by_id`
  only; `resolve()` raises `UnresolvedIdError` / `DuplicateIdError`. Completed spec bundles and done/dropped
  milestones are `historical`.
- `parse_document` (`features/documents/models/parse.py`) skips `supersedes` and `decomposed_from` on every document
  that is not a Unit anchor: an ADR's `supersedes` / `superseded_by` are neither references nor provenance and are
  checked by no rule.
- `RULE-document-reference` already has a rename precedent: a handed-off `PROP-<slug>` with exactly one
  `SPEC-<slug>` is a fixable error, rewritten by `devkit rules fix` through `services/rewrite.py`; completed specs
  are checked only as explicit targets and never rewritten; `~~strikethrough~~` keeps a mention of a removed document
  legal.
- Handoff (`features/proposals/usecases/handoff.py`) checks a graduating PADR's `ADR-<slug>` against `by_id` only.
- Playbook `aliases` live in `packages/devkit-dist/.../distribution/services/bundles/playbooks.py` and the search
  index, outside this proposal's `owns` boundary.
