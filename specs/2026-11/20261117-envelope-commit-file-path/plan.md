---
id: PLAN-envelope-commit-file-path
spec: SPEC-envelope-commit-file-path
---

# [PLAN-envelope-commit-file-path] Envelope commit accepts a workspace-relative --file path

## 1. Constitution & Invariant Review

None. The change stays inside `CAP-DLV-workflow-envelopes` §5 (one literal immediate envelope of the Unit) and the
advisory contract of `CAP-ADV-agent-advisory-protocol` and `ARCH-08-1-agent-output`; no ADR is needed.
`ADR-explicit-envelope-commits` is unchanged: the selected file and every eligibility rule stay the same.

## 2. Architecture Overview & Impact

Only `CommitEnvelopeUseCase` in `packages/devkit/src/devkit_agt/features/workflow/usecases/commit_envelope.py`
changes; the CLI adapter, repositories and services are untouched. No new dependency or feature edge.

- **Normalization**: after the Unit resolves, a `--file` value whose leading parts equal the Unit directory, as given
  (`--unit`, when relative) or as resolved workspace-relative (`ref.rel`), is reduced to the remaining parts. The
  reduced value then passes the existing literal check (`envelopes/<kind>-<NN>.yaml`, no `.`/`..`, no doubled
  separator: the original value must equal the posix join of prefix and remainder). The success payload's `file`,
  the target and the retry command use the Unit-relative form.
- **Refusal**: the shape refusal sets its own target to the Unit directory (no joined value) and its `[FIX]` names
  `uv run devkit workflow envelope commit --unit <unit> --file envelopes/<kind>-<NN>.yaml`; the code stays
  `ENVELOPE_COMMIT_INVALID` (exit `2`).

Reason for the recommended option: the feedback offered either acceptance or a better fix; doing both removes the
failure for the common spelling and keeps every other wrong value recoverable from the advisory alone. Absolute
paths stay refused (non-goal) so the literal-path guarantee is unchanged.

Design, domain and operations: unaffected; the change is a CLI input normalization inside one use case with no
persisted format, identity derivation or operational procedure (source: `commit_envelope.py`).

## 5. Error Handling & Edge Cases

- `--file <other-unit>/envelopes/review-01.yaml`, `../review-01.yaml`, `/envelopes/review-01.yaml`,
  `envelopes/../envelopes/review-01.yaml` and `envelopes/review-1.yaml` all stay `ENVELOPE_COMMIT_INVALID` before
  mutation.
- `--unit ./U` and `--unit U/` normalize through `Path` parts, so `U/envelopes/...` matches either spelling.
- `<unit>/./envelopes/...` or `<unit>//envelopes/...` is refused because it is not a literal spelling.

## 6. Verification & Test Plan

- Regression (Red then Green): `test_workspace_relative_file_inside_the_unit_commits` and
  `test_file_outside_the_unit_names_the_unit_relative_form` in
  `packages/devkit/tests/integration/features/workflow/test_envelope_commit.py` (AC-01, AC-02); the existing
  `test_nonliteral_paths_refuse`, `test_exact_commit_idempotence_and_evidence` and `test_cli_json_text_and_errors`
  cover AC-02 and AC-03.
- Checks: `just lint-check`, `uv run devkit rules check --ci --base main`, `just test-affected --base main`.
