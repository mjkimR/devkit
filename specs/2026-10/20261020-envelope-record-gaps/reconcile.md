---
reconcile_id: REC-envelope-record-gaps
feature: SPEC-envelope-record-gaps
status: pending
targets:
  - file: docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-spec-rules.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
---

# Reconcile: `SPEC-envelope-record-gaps`

## Living Spec changes

- `CAP-DLV-workflow-envelopes`: summary; section 1 (a `reverify` names a `review-NN.yaml` or `challenger-NN.yaml`
  round; the deciding state of `review` and `challenger`; the review state ignores challenger reverifies); section 1.1
  (`settles` in the answer example, the `answer` table row and the item contract); section 2 (`--findings-file`
  refusal for `challenger`, `--from` with challenger files and its refusal fix, the new `--settle` row, the key order);
  section 3 (`review=<file>` on reverify lines; JSON `review` and `settles`).
- `CAP-DLV-delivery-workflows` rule 15: Planning closes each round with a reverify of the `challenger-NN` round (also at
  `medium`), the round count of unmarked rounds and answer folds, and the `plan-accept` request showing each challenger
  round with its closing reverify.
- `CAP-DLV-proposal-incubation`: the `target_area` row states the accepted boundary forms, the nearest-existing-parent
  form, `RULE-proposal-boundaries` and its clearing before the `plan-accept` request.
- `CAP-GOV-spec-rules`: eleven rules; the catalog row and section 3.12 for `RULE-proposal-boundaries` (warning), the
  summary renumbered to 3.13.
- `CAP-HARN-agent-guidance` (outside the proposal's listed areas; its rule asset list would otherwise be stale): the
  `proposal-boundaries` rule asset.

Entrypoints: the existing entrypoints (`packages/devkit/src/devkit/workflow/unit/envelope/`, `cli/envelope.py`,
`packages/devkit-spec/src/devkit_spec/rules/`, `bundle/rules/`) already cover every changed path; none added.

No ADR change: the three accepted ADRs decide the design; no `docs/architecture/` statement changes (layering holds).

## Source feedback

- `FB-review-loop-round-count-across-procedure-change`: resolved (Disposition appended; verified by
  `test_record_gaps_procedure.py` and the initial code review).
- `FB-review-round-count-before-markers`: the same observation, fully addressed by the same review-loop text; its file
  lies under `docs/proposals/PROP-draft-direct-acceptance/`, outside this unit's write boundary, so it is left
  `promoted` for the Host to resolve.
- `FB-challenger-findings-stay-open`, `FB-answer-envelope-no-slot-for-settled-assumptions` and
  `FB-proposal-boundaries-unchecked`: fully addressed by AC-01 to AC-05, AC-06 and AC-07, and AC-08 to AC-10; their
  files lie in other spec bundles, outside the write boundary, so they are left for the Host to resolve.

## Deferred work

None retained. Deploying the new rule into this repository's `.devkit/` installation is the Host's `devkit sync` after
integration (Non-Goal 5).
