---
id: FB-worker-envelope-stage-unchecked-at-write
title: Worker envelope --stage is not checked against the workflow at write time
scope: repo
kind: suggestion
category: tool-error
target: devkit workflow envelope worker
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-30
---

# [FB-worker-envelope-stage-unchecked-at-write] Worker envelope --stage is not checked against the workflow at write time

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `devkit workflow envelope worker --stage <text>` refuses only an empty value or `-`. Any other
  text is written; stage membership is checked only later by `devkit workflow envelope commit`. An envelope whose
  stage the bound workflow does not define is evaluated as held from the first stage, so it holds every gate,
  `plan-intent` included.
- **Proposed Procedure**: Refuse at write time a `--stage` the unit's bound workflow does not define, with a fix naming
  the stages, as `envelope commit` already does.
- **Expected Benefit**: A worker that guesses a stage name (for example when `devkit workflow next` prints
  `[STAGE: - complete=yes]`) learns it at write time instead of leaving a unit whose every gate is held.
- **Cost & Risk**: A unit bound to an invalid or missing workflow definition would need the current lenient path;
  the help text says the definition is otherwise not loaded at write time.
- **Attempted**: Hypothesis from a static code trace in this Planning; no envelope with an unknown stage was written.

## Diagnostic Details

- **Reproduction**: Not reproduced; traced in code.
- **Expected / Actual**: Expected a refusal for an undefined stage; the contract check rejects only `""` and `-`.
- **Versions**: devkit at `fdba6646`.
- **Conditions**: Any unit; most likely in a Planning run under `plan-accept=auto`, where `next` names no stage.
- **Workarounds Attempted**: `PROP-git-operator-planning-completion-route` names `direction-handoff` in worker
  guidance for that case.
- **Related Assets**: `packages/devkit/src/devkit_agt/features/workflow/services/envelope/authoring.py`
  (`_check_contract`), `packages/devkit/src/devkit_agt/features/workflow/services/envelope/commit.py`,
  `packages/devkit/src/devkit_agt/features/workflow/usecases/evaluate.py` (held-from index for an unknown stage),
  `packages/devkit/tests/integration/features/workflow/test_envelope_hold.py`.

## Evidence

```text
Scout trace (envelopes/scout-01.yaml, finding 1): compose_envelope refused "-" and "" and accepted
"no-such-stage"; evaluate maps stage index -1 to held_from 0; commit.py checks stage membership.
```
