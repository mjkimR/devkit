---
id: PADR-post-batch-test-run
title: One test run on main after a local-orchestrated batch
summary: For semantic conflicts a conflict-free merge can carry, we run the integrated-content tests once on main after every unit of a local-orchestrated run is finished (integrated, blocked, awaiting the user or continued in direct), to surface them before nightly CI, accepting one extra run per batch.
proposal: PROP-integration-merge-moved-target
status: draft
created_at: 2026-10-30
supersedes:
  - ADR-test-selection-and-ci
---

# [PADR-post-batch-test-run] One test run on main after a local-orchestrated batch

- **Status**: Draft
- **Date**: 2026-10-30

This decision supersedes only one clause of `ADR-test-selection-and-ci`: "The final integration content is verified
after incorporating a moved base or resolving conflicts; merging the same verified content does not trigger another
test run." Affected-test selection, the full-suite fallback and the nightly and release CI of that decision remain in
force.

---

## 1. Context & Problem Statement

With `PADR-moved-target-merge`, the integrating command merges a conflict-free moved target itself and runs only CI
rules on the merged result; tests and review ran on the source. Two units integrated one after the other can each pass
their own tests and still break together, and nothing runs the tests on the combined head until nightly CI. A
local-orchestrated run integrates several units in a row, so its end is the point where the combined head is known.

## 2. Decision Drivers

- A semantic conflict may surface later, but not stay hidden (user direction).
- One run on the integrated head, not an aggregation of the units' earlier results (user direction).
- Shipped skills follow each consuming repository's verification policy; the bundle prescribes no command.
- No automatic revert; a failure becomes follow-up work.

## 3. Considered Options

- **Rely on nightly CI** (rejected): the combined head stays untested for up to a day and a failure is not attributed
  to the batch.
- **Re-test each unit after its merge** (rejected): repeats work per unit, the cost the light merge removes.
- **One run after the batch, in `spec-orchestrate` Completion** (selected): the Host runs the repository's
  integrated-content verification once on `main`, with no new CLI command.
- **A CLI helper that runs and records the batch tests** (rejected): devkit would need to own the test command, which
  is repository policy, and the result is a conversation report, not a record.
- **The full suite once per batch** (rejected by the user): also catches selection misses, but costs a full local run
  per batch that `ADR-test-selection-and-ci` leaves to nightly CI.
- **Wait until every unit the run started is integrated** (rejected by the user): a blocked unit can stay open for
  long, leaving the integrated units untested on `main` until nightly CI.

## 4. Decision Outcome

Chosen option: one run after the batch in `spec-orchestrate` Completion, because it meets both user constraints with a
skill change only.

- When a local-orchestrated run starts its first unit, the Host notes the base branch HEAD as the batch start.
- Once every unit the run started is finished and no worker turn of the run is still running, the Host runs the
  repository's verification for integrated content once on the base branch HEAD, scoped from the batch start when the
  repository's selector supports a base. In this repository that is `just test-affected --base <batch start>`,
  keeping its `mode=full` fallback; nightly CI still runs the full suite.
- A unit counts as finished when it is integrated, ends blocked with its problem recorded, waits for a user decision
  (its last `worker` envelope is `needs_input`), or continues in `direct` mode. The run thus tests what it integrated.
- Outside a batch run (a unit continued in `direct`, or any `direct`-mode integration), a conflict-free CLI-built
  merge is covered by its source verification plus the CI rules on the merged result; the combined head is tested by
  a later batch run or by nightly CI. The repository's verification policy states this in place of incorporating a
  moved base before integration.
- After a context loss the Host recovers the batch start as the first parent of the run's earliest
  `chore(merge): integrate <branch> into <base branch>` commit on the first-parent history; only when that fails it
  runs the selector's full fallback.
- The Host reports the result in the conversation with the tested head and the command. A failure is reported with
  its evidence and recorded as feedback for follow-up work; nothing is reverted automatically.
- A run that integrated no unit runs nothing.

## 5. Consequences

- **Positive**: semantic conflicts between the batch's units surface before nightly CI and are attributed to the
  batch.
- **Negative / Risks**: one extra test run per batch; a selection miss the affected selector does not cover still
  waits for nightly CI.
- **Follow-ups**: Development states this repository's command and the coverage outside a batch run in `AGENTS.md`,
  `docs/development/ci-cd.md` and `docs/development/workflow.md`, and replaces "Integration incorporates a moved base"
  in `CAP-HARN-agent-guidance`.

## 6. Confirmation

- Bundle asset tests check that `spec-orchestrate` Completion names the batch run and its finished-unit rule, and that
  `spec-integrate` step 1 is conditional (`packages/devkit-spec/tests/integration/bundles/spec/`).
- Review only for the Host's conversation report.
