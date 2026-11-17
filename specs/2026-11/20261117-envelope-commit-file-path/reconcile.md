---
reconcile_id: REC-envelope-commit-file-path
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md
    resolution: modified
formal_docs:
  design: "none: one use case normalizes an input path; no component, mechanism or interface shape changes"
  domain: "none: no domain concept, identity or lifecycle is introduced or renamed"
  operations: "none: no runbook, symptom or action owner is affected"
---

# Reconciliation: `SPEC-envelope-commit-file-path`

## Contract comparison

- `CAP-DLV-workflow-envelopes` §5 clause 3 (AC-01, AC-02): now states that `--file` is Unit-relative, that a value
  starting with the Unit directory (as given or resolved workspace-relative) selects the same record with results
  and retries in the Unit-relative form, and that a wrong-shape `--file` targets the Unit with a `[FIX]` naming
  `--file envelopes/<kind>-<NN>.yaml`. This matches `CommitEnvelopeUseCase` and `_unit_relative` in
  `packages/devkit/src/devkit_agt/features/workflow/usecases/commit_envelope.py`.
- `CAP-DLV-cli-and-output`: unaffected; its synopsis and success sentinel already show the Unit-relative
  `envelopes/NAME.yaml`, which remains the reported `file`, and no code is added (`ENVELOPE_COMMIT_INVALID`, exit `2`).
- The spec skill's envelope reference §5 (bundle source) and the workflow definitions: unaffected; they name the
  canonical `--file envelopes/<kind>-<NN>.yaml` form, which keeps working unchanged (AC-03).
- Use cases, architecture and glossary: unaffected; no new behavior beyond the CLI input normalization.

## Source feedback

- `FB-envelope-commit-file-path-doubled`: resolved; both suggestions are implemented and verified by the regression
  tests. Disposition appended to its file.
