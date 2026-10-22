---
reconcile_id: REC-feedback-guidance-fixes
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-spec-bundles.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
---

# Reconcile: `SPEC-feedback-guidance-fixes`

- `CAP-DLV-proposal-incubation`: section 4.4 states that a PADR has no withdrawn status and that a PADR withdrawn
  before `plan-accept` is deleted in the fold commit and named in the Planning decisions; the 4.6 table gains the
  carried-contract row and the notes section number; the report section describes `--template`,
  `spec_proposal_report_template`, the `--template`/`--body-file` exclusivity and the field-class refusal messages;
  the `PROPOSAL_REVIEW_INVALID` row names the template routes.
- `CAP-DLV-spec-bundles`: the 4.3 `spec.md` skeleton lists `5. Carried Proposal Contract` and the notes numbering.
- `CAP-DLV-workflow-envelopes`: the `--from` row states the reconcile-check `[FIX]`.
- `CAP-HARN-agent-guidance`: the `spec-review-proposal` row lists `spec_proposal_report_template`.
- The answer-correction procedure is guidance only (`references/worker-records.md`); `CAP-DLV-workflow-envelopes`
  already allows several answers naming one worker envelope, so no contract text changes for it.
- Stories: none changed; no new user outcome. Glossary: no new domain term.

## Source feedback

All five sources were `open` direct-fix sources and are now `resolved`, each with a Disposition naming this spec:

- `FB-proposal-report-template-discovery`: AC-01 to AC-05; `test_proposal_report.py` (CLI template, exclusivity,
  read-only MCP tool, field-class refusals) and `test_cloud_guidance.py` (skill renderings).
- `FB-reverify-fix-omits-reconcile-check`: AC-06; `test_envelope_record_gaps.py`. The `spec-delegate` Step 6
  sentence its suggestion also names is outside this unit's write scope; `references/effort.md` already states the
  reconcile-check route, and the `[FIX]` now names it at the point of failure.
- `FB-padr-withdrawal-unspecified`: AC-07; `references/planning.md` step 2 and `CAP-DLV-proposal-incubation` 4.4.
- `FB-answer-correction-unrecorded`: AC-08; `references/worker-records.md` section 2 and
  `test_a_later_answer_corrects_an_answered_question`.
- `FB-handoff-skeleton-scenario-placement`: AC-09; `test_proposal_body.py` and
  `test_mixed_acceptance_and_non_goals_carry_as_contract`.

## Deferred Work

None.
