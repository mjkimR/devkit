---
id: PLAN-reverify-carry-latest-state
spec: SPEC-reverify-carry-latest-state
---

# Technical Plan: `SPEC-reverify-carry-latest-state` Reverify carries the latest closing state

## 1. Architecture Overview & Impact
- Target Area: `devkit-agt` workflow envelope authoring (`features/workflow/models/envelope.py`,
  `features/workflow/services/envelope/authoring.py`), the `--from` row of `CAP-DLV-workflow-envelopes`, and the spec
  bundle's `planning.md` closing step.

## 2. Component Breakdown & Interface Contracts
- `Envelopes.closing_state(name)`: the last reverify whose `review` is `name`, or `None`. `round_state` reuses it, so
  `--from latest` and the evaluated deciding state share one rule.
- `carried_findings`: when `--from` names a `review` or `challenger` file, carry the findings of
  `envelopes.closing_state(<file name>)` (the current segment's envelopes) when present, else the file's own findings;
  `review` stays the round's file name. A `reverify` file and `latest` are unchanged.
- `--resolve`/`--waive` numbering is over the carried list, which keeps the round's finding order.
- Guidance: `planning.md` step 3 says a later reverify of the same round keeps earlier resolutions and waivers;
  `review-loop.md` needs no change because its text names the command, not its carry rule.

## 3. Verification & Test Plan
- Integration tests in `packages/devkit/tests/integration/features/workflow/test_envelope_record_gaps.py` for AC-01 to
  AC-04 through the CLI.
- `just lint devkit-agt`, `just check devkit-agt`, `just test-affected`, `just rules-check`.
