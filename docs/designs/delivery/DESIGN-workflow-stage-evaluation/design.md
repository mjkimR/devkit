---
id: DESIGN-workflow-stage-evaluation
title: "Workflow stage evaluation order"
status: active
summary: "Walks one sdd-spec-feature Unit through devkit workflow next: segment and return voiding, hold, stage policy, exit checks, gate and stop at the first unmet stage; contracts stay with the delivery capabilities."
area: delivery
related_capabilities: [CAP-DLV-workflow-orchestration, CAP-DLV-human-interaction, CAP-DLV-workflow-envelopes, CAP-DLV-workflow-definitions]
entrypoints:
  - packages/devkit/src/devkit_agt/features/workflow/usecases/evaluate.py
  - packages/devkit/src/devkit_agt/features/workflow/models/decision_records.py
---

# [DESIGN-workflow-stage-evaluation] Workflow stage evaluation order

A Unit's stage depends on several record sources at once: stage and gate policy, exit checks, decision records,
envelopes, holds and returns that void earlier evidence. Each capability states its own rule, but none shows the order
in which `devkit workflow next` combines them on one Unit, so a reader cannot predict which source decides a reported
`[STAGE]`. This walk-through follows `evaluate_definition` in
[evaluate.py](../../../../packages/devkit/src/devkit_agt/features/workflow/usecases/evaluate.py) over one real Unit.

## Evaluation order

`evaluate_definition` reads the anchor, then builds an evaluator that prepares every record source before any stage
is visited:

1. **Segment.** Decision records count only when written in the bound workflow with a sequence above the current
   segment's start (`Decisions.segment` in
   [decision_records.py](../../../../packages/devkit/src/devkit_agt/features/workflow/models/decision_records.py);
   `CAP-DLV-human-interaction` §5, last paragraph).
2. **Accepted returns.** Each accepted `return:<stage>` record becomes a pair of sequence number and target stage
   index (`Decisions.accepted_returns`).
3. **Hold.** Unresolved problems, unanswered questions and malformed worker envelopes are read over every envelope of
   the Unit, whatever their segment, and turned into the first stage index whose gate is held
   (`CAP-DLV-workflow-envelopes` §4).
4. **Current envelopes.** `current_envelopes` keeps the envelopes scoped to this workflow and segment, then drops
   those a later accepted return re-opened (`CAP-DLV-human-interaction` §5 Returns).
5. **Gate policy check.** The evaluator refuses a configured approval policy the definition does not accept
   before any stage is evaluated (`CAP-DLV-workflow-orchestration` §3).

The stage loop then visits stages in definition order. For each stage it applies, in this order:

1. An `exception` stage is never evaluated (`CAP-DLV-workflow-definitions` Stage Fields).
2. Stage policy `stages.<id>=off` skips the stage before any check or gate (`CAP-DLV-workflow-orchestration` §3
   Stage Policy).
3. Gate policy `approvals.<gate>=off` skips a gated stage (`CAP-DLV-workflow-orchestration` §3).
4. Every exit check is evaluated; disk checks read the current envelopes, a human check reads a decision record
   whose approval no later return voided. Entry checks are not
   evaluated (`CAP-DLV-workflow-definitions` Stage Fields).
5. The gate status comes from policy `auto`, `--given` or an accepted decision record (`CAP-DLV-human-interaction`
   §5 Approve gate).
6. A hold reaching this stage's index overrides the gate to unsatisfied with `held=yes`; when the exit checks hold,
   the unmet `envelope-hold` check takes the gate's place (`CAP-DLV-workflow-envelopes` §4).
7. An unsatisfied gate becomes the unmet `gate:<gate>` check only when no exit check is unmet
   (`CAP-DLV-human-interaction` §5 Approve gate).
8. With nothing unmet and the gate satisfied, the stage is done and its gate source is kept for `[GATE_PASSED]`.
   Otherwise an `optional` stage is passed over (`CAP-DLV-workflow-definitions` Stage Fields), and any other
   stage becomes current: the loop records its unmet checks, skill, delegation, gate, waiting reason, requests and
   stale approvals, then stops.

After the loop, the handoff is evaluated only when no stage is current, and unanswered questions add their requests
and replace the waiting reason (`CAP-DLV-workflow-orchestration` §3 The `handoff` Gate, `CAP-DLV-workflow-envelopes`
§4).

## Worked example: a completed spec Unit after a return

The sample Unit is `specs/2026-11/20261116-formal-document-kinds/`, anchored by `SPEC-formal-document-kinds` and
bound to [sdd-spec-feature](../../../../packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/workflows/sdd-spec-feature.md)
with an empty `workflow_history` (segment `0`). The project sets `[workflow.approvals] dev-integration = "auto"`.
Its records:

| Record | Stage | Time |
| --- | --- | --- |
| `decisions/01-gate-plan-accept.yaml` (approve, accept) | `direction-handoff` | `2026-11-16T05:36:43.097533Z` |
| `decisions/02-return-build-verify.yaml` (return, accept) | `build-verify` | `2026-11-16T06:15:49.651667Z` |
| `review-01`, `reverify-01`, `review-02` | `review-refine` | `05:59:48` to `06:06:14` |
| `reconcile-check-01`, `reconcile-check-02` | `living-spec-draft` | `06:10:38`, `06:11:39` |
| `feedback-01`, `final-report-01` | `collect-feedback`, `final-change-report` | `06:13:33`, `06:14:22` |
| `review-03`, `reconcile-check-03`, `feedback-02`, `final-report-02` | same stages | `06:19:14` to `06:22:22` |
| `worker-01` (`status: completed`, no problem, no questions) | `integrate` | `06:22:59` |

Running `uv run devkit workflow next --unit specs/2026-11/20261116-formal-document-kinds` evaluates it as follows.

1. **Segment and returns.** Both decision records belong to segment `0` of `sdd-spec-feature`. The one accepted
   return targets `build-verify`, stage index `2`.
2. **Hold.** `worker-01` reports no problem and no question, and no worker envelope is malformed, so the hold is empty
   and no gate is held.
3. **Return voiding.** The return's `at` is written to the microsecond, so its span ends one microsecond after
   `06:15:49.651667Z` (`record_instant`). Every envelope for `build-verify` or a later stage whose `created_at` starts
   before that end is void: `review-01`, `reverify-01`, `review-02`, `reconcile-check-01`, `reconcile-check-02`,
   `feedback-01` and `final-report-01`. Only the round-two envelopes count. Had the return been written to the second
   (`2026-11-16T06:15:49Z`), its span would cover that whole second, and an envelope stamped `06:15:49.700000Z` would
   also be void (`CAP-DLV-human-interaction` §5 Returns). The approval record targets
   `direction-handoff`, which is no stage of this definition, so the return does not void it; no stage reads it either.
4. **Gate policy check.** `dev-integration` accepts `ask` and `auto` in the definition's `gates` mapping; the
   configured `auto` passes.
5. **Stages `intent` to `final-change-report`.** No stage policy is set and none of these stages is gated. Each
   stage's exit checks hold: `envelope-review-passed` reads `review-03`, `envelope-completed(reconcile-check)` reads
   `reconcile-check-03`, and the `envelope-check-pass` checks read `feedback-02` and `final-report-02`. All seven are
   done.
6. **Stage `integration-approval`.** Its exit list is empty, its gate `dev-integration` is satisfied by policy
   `auto`, and no hold reaches it. The stage is done, reported as
   `[GATE_PASSED: dev-integration stage=integration-approval policy=auto source=policy]`.
7. **Stage `integrate`.** `frontmatter(reconcile.md status resolved)` and `anchor-status-completed` hold.
   `lint-ci-clean` is a `runner` check passed neither by `--given` nor by a record, so it stays unmet with
   `evaluated=no`. The stage has no gate and is not `optional`, so it becomes current. Its only unmet check is a
   runner check, so the waiting reason is `[WAITING: runner lint-ci-clean]`. No accepted approval names a later
   stage, so no `[STALE_APPROVAL]` appears. The loop stops; `merge` is not evaluated.
8. **After the loop.** A current stage exists, so no handoff is evaluated, and no question adds requests.

The output at this state:

```text
[WORKFLOW: sdd-spec-feature unit=specs/2026-11/20261116-formal-document-kinds status=completed bound=yes]
[DONE: intent specify build-verify review-refine living-spec-draft collect-feedback final-change-report integration-approval]
[GATE_PASSED: dev-integration stage=integration-approval policy=auto source=policy]
[STAGE: integrate human_gate=- role=developer isolation=none]
[UNMET: lint-ci-clean]
[CHECK: lint-ci-clean class=runner evaluated=no detail="declared for runner; not evaluated"]
[NEXT_SKILL: spec-integrate]
[RETURNS: build-verify when="defects beyond integration scope"; exception when="retry caps"]
[WAITING: runner lint-ci-clean]
```

Two variations of the same state show where the hold step acts. If `worker-01` carried an unresolved problem, the
hold would start at `integrate`: the `dev-integration` gate before it stays passed, `integrate` and `merge` have no
gate to hold, and the hold shows as a `[BLOCKED]` line and a refused handoff once the Unit completes. If the problem
were recorded at `final-change-report` instead, `integration-approval` would report `held=yes` and the unmet
`envelope-hold` check, and `integrate` would not be reached.

## Why only the first unmet stage is reported

The loop stops at the first stage that is neither done, skipped nor passed over (`break` in `evaluate_definition`).
No check, gate, request or waiting reason of a later stage is computed, so `[STAGE]`, `[UNMET]`, `[NEXT_SKILL]` and
`[REQUEST]` all describe that one stage. This is the diagnosed stage of `CAP-DLV-workflow-orchestration` §1 item 2.
Gates follow the same order inside a stage (`CAP-DLV-human-interaction` §5 Approve gate), so evaluating a later stage
would ask approvals for work that the current stage has not produced yet.

The one fact `next` reads about later stages is `approvals_after`: accepted approvals of a later stage that no
return voided. They appear as `[STALE_APPROVAL]` lines and keep counting until a `return` record voids them; `next`
records no return (`CAP-DLV-human-interaction` §5 Returns).

## Authority boundary

`CAP-DLV-workflow-orchestration` owns the delivery model, stage and gate policies and the handoff gate.
`CAP-DLV-workflow-definitions` owns stage fields and checks. `CAP-DLV-workflow-envelopes` owns envelope scoping,
authoring timestamps and the hold (§4). `CAP-DLV-human-interaction` §5 owns how answers, returns, return voiding and
timestamp precision apply. `CAP-DLV-cli-and-output` owns the sentinel lines, their order and exit codes. The
[workflow reference](../../../development/reference/workflow.md) owns command syntax, configuration and the module
map.

## Update triggers

- `evaluate_definition`, `current_envelopes`, `record_instant` or `Decisions` change the order or inputs of the
  evaluation, the hold or the waiting reason.
- The sample Unit's records change. Recheck the example with
  `uv run devkit workflow next --unit specs/2026-11/20261116-formal-document-kinds` and compare its output with the
  block above.
