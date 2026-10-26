---
reconcile_id: REC-reverify-carry-latest-state
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md
    resolution: modified
---

# Reconcile: `SPEC-reverify-carry-latest-state`

- `CAP-DLV-workflow-envelopes` section 2, `--from` row: a named `review-NN.yaml` or `challenger-NN.yaml` carries its
  closing state (the last reverify of the current segment whose `review` names the file, else the file's own
  findings); a `reverify-NN.yaml` carries its own findings and `review`. `--from latest`, the `--resolve`/`--waive`
  rows and section 3 (deciding state) are unchanged and still match the code, because `round_state` now delegates to
  the same `closing_state` lookup without changing its result.
- No use case, architecture document or glossary term changes: the change refines one authoring flag of an existing
  command.
- Agent guidance: the spec bundle's `skills/spec/references/planning.md` step 3 adds that a later reverify of the same
  round starts from its last reverify; `review-loop.md` names the command only and needs no change.

## Source feedback

- `FB-reverify-reopens-earlier-resolutions`: resolved; the Disposition names this spec and the verifying tests.

## Deferred work

None.
