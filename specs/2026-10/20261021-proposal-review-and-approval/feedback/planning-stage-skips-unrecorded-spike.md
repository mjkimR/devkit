---
id: FB-planning-stage-skips-unrecorded-spike
title: Planning next can skip an unrecorded spike
scope: repo
kind: friction
category: spec-ambiguity
target: devkit workflow next
skill: spec
agent: codex
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-21
---

# [FB-planning-stage-skips-unrecorded-spike] Planning next can skip an unrecorded spike

## 1. Friction

- **Context**: First medium Planning turn after a Host recorded plan-intent.
- **Expectation**: Stage guidance should distinguish completed investigation from an unchecked spike.
- **Actual**: `workflow next` reported spike done while the proposal was draft and had no support-role envelope.
- **Workaround**: Followed the explicit Planning procedure and Host handoff, performed the spike and mandatory challenger.
- **Suggestion**: Clarify in the stage output or guide that a condition-free spike completion is not Planning evidence.
  An engine change needs separate review because low-effort Planning has no challenger requirement.

## Diagnostic Details

- **Reproduction**: Run `devkit workflow next --unit <proposal>` after first plan-intent on a draft proposal.
- **Expected / Actual**: Expected a Planning work pointer; actual stage was collect-feedback with spike in DONE.
- **Versions**: Assigned branch initial revision `0269cd9b103c5f3dc2633f8119528fc64890ed56`.
- **Conditions**: Local-orchestrated Codex worker, medium effort, first turn.
- **Workarounds Attempted**: Read planning.md and executed its full procedure; no workflow mutation workaround.
- **Related Assets**: `packages/devkit-spec/src/devkit_spec/bundle/workflows/sdd-proposal.md`.

## Evidence

```text
WORKFLOW: sdd-proposal status=draft bound=yes
DONE: intent-proposal spike
STAGE: collect-feedback
UNMET: envelope-check-pass(feedback swept)
```

## Disposition

Directly resolved by `SPEC-feedback-quick-fixes` as the wording-only clarification the suggestion asked for. The `spec` skill's Planning reference (step 3) and the `spec-next` workflow-signals reference state that `spike` has no exit check, so its `[DONE]` listing is not Planning evidence; the `scout` and `challenger` envelopes and their `reverify` recorded at `spike` are. `CAP-DLV-delivery-workflows` states the same. No workflow definition or `devkit workflow next` logic changed.

Verification: `test_role_contracts.py` asserts both texts (52 passed); the full suite passed (4461 passed, 14 skipped). Integration remains a separate Host step.
