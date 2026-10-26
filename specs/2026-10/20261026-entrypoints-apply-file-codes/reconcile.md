---
reconcile_id: REC-entrypoints-apply-file-codes
status: resolved
targets:
  - file: docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md
    resolution: modified
---

# Reconcile: `SPEC-entrypoints-apply-file-codes`

## Living Spec changes

- `CAP-TRACE-code-entrypoints`, section 3.5 rule 3: a `--code` path equal to a folded candidate unfolds it (AC-02); one
  that contains no candidate of a document but lies under one becomes a candidate of that document with the nearest
  candidate's provenance (AC-01); one that still matches no candidate (of the `--target` documents with `--apply`)
  refuses the run with `SPEC_ENTRYPOINTS_CODE_UNMATCHED` before anything is written, with the reason for a refusal
  over a notice (AC-03). Sections 4.4 and 4.5 add the exit cause and the code; section 4.6 lists
  `adopt_nested_selectors` and `unmatched_selectors`.

## No-impact documents

- `spec-entrypoints` skill: its procedure (keep 1-3 doorway files, apply with `--target` and `--code`) is unchanged
  and now works as written; no text changes, so no `devkit sync` output.
- `UC-keep-the-living-spec-consistent`, `UC-find-the-right-documents` and `CAP-DOCS-document-lookup`: their steps
  and codes do not cover `--code` selection; `devkit spec list --file` is unchanged.
- Handbook traceability pages name no `derive` error codes and show only directory `--code` examples, which keep
  their behavior.

## Source feedback

- `FB-entrypoints-apply-ignores-file-codes`: resolved by this spec; status `resolved` with a Resolution section,
  verified by `test_file_code_under_a_directory_candidate_is_applied`, `test_selected_folded_candidate_is_applied`
  and `test_unmatched_code_is_refused_before_writing` (envelope `green-01.yaml`).

## Entrypoints

- `CAP-TRACE-code-entrypoints` already declares `packages/devkit-spec/src/devkit_spec/features/entrypoints/`, which
  covers every changed source file of the feature. The other `derive` candidates were rejected in review:
  `base/errors.py` is a shared error module and the entrypoints tests are tests, not doorways.
