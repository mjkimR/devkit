---
reconcile_id: REC-envelope-answer-decider
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-cli-and-output.md
    resolution: modified
---

# Reconcile: `SPEC-envelope-answer-decider`

- `CAP-DLV-workflow-envelopes` section 1.1: the answer example carries `by: user`, and the `answer` row states the
  optional `by` (`user`, `host` or `policy`; absent or `null` unstated; any other value malformed). Section 2: the
  `--answers-to`/`--answers-file` row names the entry shape with `by?` and refuses an unknown `by` with
  `ENVELOPE_ITEMS_INVALID`; the `--resolve` row adds `ENVELOPE_FINDING_CLOSED` for a `--resolve N` or `--waive N`
  naming an already `resolved` or `waived` carried finding, checked after the range, with `[TARGET]` listing every
  such flag and number, the same `[DETAIL]` lines and nothing written. Section 3 (`--details` bodies) needs no change:
  it already restores complete bodies, which now include `by`.
- `CAP-DLV-cli-and-output` error table: a row for `ENVELOPE_FINDING_CLOSED` (`EnvelopeFindingClosedError`,
  `INPUT_ERROR`, exit `2`), and the authoring row names an unknown answer `by` under `ENVELOPE_ITEMS_INVALID`.
- Quick reference `docs/development/reference/workflow.md`: the reverify and answer examples note "open findings only"
  and the optional `by`.
- No use case, architecture document or glossary term changes: the change adds one optional field and one refusal to
  existing authoring commands; "decider" is used descriptively, not as a new domain term.
- Agent guidance: the spec bundle's `worker-records.md` §2 example and a bullet define `by`; the `spec-delegate`
  `payload.md` (`planning-worker` row) and `worker.md` (Questions) hand the rewritten answers over with `by` per
  answer; `planning.md` step 3 states the closed-number refusal. `devkit sync` updated `.devkit/installation.json`.
- Entrypoints: `devkit spec entrypoints derive` proposed only the `_Boundary:` directories (the whole
  `devkit_agt.features.workflow` feature, test trees, guidance directories and `.devkit/installation.json`), each
  broader than either capability or not a doorway; none is applied, and neither capability's `entrypoints` changes.

## Source feedback

- `FB-answer-envelope-has-no-decider`: resolved; the Disposition names this spec and the verifying tests.
- `FB-reverify-resolve-overwrites-waiver`: resolved; the Disposition names this spec and the verifying tests.

## Deferred work

None.
