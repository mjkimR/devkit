---
id: PLAN-envelope-answer-decider
spec: SPEC-envelope-answer-decider
---

# Technical Plan: `SPEC-envelope-answer-decider` Record the decider of each answer and guard reverify closures

## 1. Architecture Overview & Impact
- Target Area: `devkit-agt` workflow envelopes (`features/workflow/models/envelope.py`, `models/errors.py`,
  `services/envelope/model.py`, `services/envelope/authoring.py`, `cli/envelope.py` help text); the answer and
  reverify rows of `CAP-DLV-workflow-envelopes`, the authoring-error row of `CAP-DLV-cli-and-output`; the spec
  bundle's `worker-records.md`, `planning.md` and the `spec-delegate` `payload.md` and `worker.md`.

## 2. Component Breakdown & Interface Contracts
- `Answer.by: str = ""` with `DECIDERS = ("user", "host", "policy")`. `to_dict()` writes `by` after `decision` and
  `constraints` only when set, so files without it render as before.
- `ANSWER_KEYS` gains `by`. `parse_answer` reads `by` (absent or `null` is empty); any other value outside `DECIDERS`
  raises `EnvelopeFormatError` naming the allowed values. `parse_answers` already wraps it as `ENVELOPE_ITEMS_INVALID`
  (`[TARGET] --answers-file`) and the loader as `ENVELOPE_INVALID`; the `--answers-file` fix and help mention `by`.
- `EnvelopeFindingClosedError(AuthoringError)`, code `ENVELOPE_FINDING_CLOSED`. `apply_resolutions` first checks every
  number's range (unchanged `ENVELOPE_FLAG_INVALID`), then collects each `--resolve N` and `--waive N` whose carried
  finding is not `open` and raises one error whose `target_files` are `--resolve N`/`--waive N` and whose details
  number the carried findings, before anything is applied or written.
- Guidance: worker-records §2 example and a bullet defining `by`; payload and worker references name `by` per
  rewritten answer; planning step 3 says a closed number is refused.

## 3. Verification & Test Plan
- Integration tests through the CLI in
  `packages/devkit/tests/integration/features/workflow/test_envelope_answer_decider.py` for AC-01 to AC-07, written
  before the code (Red, then Green).
- A guidance test in `packages/devkit-spec/tests/integration/bundles/spec/` for AC-08.
- `just lint devkit-agt`, `just check devkit-agt`, `just test-affected`, `just rules-check`.
