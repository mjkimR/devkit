---
id: FB-handoff-carries-proposal-stage-decision
title: Spec handoff carries a plan-accept decision record whose stage is not in the spec workflow
scope: repo
kind: question
category: other
target: devkit spec proposal handoff
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-11-16
---

# [FB-handoff-carries-proposal-stage-decision] Spec handoff carries a plan-accept decision record whose stage is not in the spec workflow

## 1. Friction / Question (friction, question)

- **Context**: Reading decision records of a sample spec Unit for the workflow stage evaluation design.
- **Expectation**: A decision record bound to `sdd-spec-feature` names a stage of that definition.
- **Actual**: Nature: record consistency. Handed-off Units carry `decisions/01-gate-plan-accept.yaml` with `workflow: sdd-spec-feature` and `stage: direction-handoff`, which is a proposal-workflow stage. It is never read or voided, so it is harmless today, but a reader of the evaluation order cannot tell whether it is intended.
- **Workaround (or Interpretation Chosen)**: The design treats the record as unread and not voided, as the source does.
- **Suggestion**: Confirm whether the carried record should keep the proposal workflow binding or its stage.

## Diagnostic Details

- **Reproduction**: Read-only record and evaluate.py reading.
- **Expected / Actual**: A stage of the bound definition, or the proposal binding.
- **Versions**: repository head of the formal-document-coverage Development branch.
- **Conditions**: every proposal handoff
- **Workarounds Attempted**: not attempted
- **Related Assets**: packages/devkit/src/devkit_agt/features/workflow/usecases/evaluate.py

## Evidence

```text
specs/2026-11/20261116-formal-document-kinds/decisions/01-gate-plan-accept.yaml: workflow sdd-spec-feature, stage direction-handoff
specs/2026-11/20261116-formal-document-coverage/decisions/01-gate-plan-accept.yaml: same shape
```
