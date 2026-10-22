---
id: FB-handoff-skeleton-scenario-placement
title: Handoff places proposal validation scenarios under Non-Goals
scope: repo
kind: friction
category: tool-error
target: packages/devkit-spec/src/devkit_spec/proposals/handoff.py
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-21
---

# [FB-handoff-skeleton-scenario-placement] Handoff places proposal validation scenarios under Non-Goals

## 1. Friction / Question

- **Context**: Normalizing an accepted proposal's generated Development skeleton.
- **Expectation**: Carried positive acceptance scenarios are identifiable separately from excluded scope.
- **Actual**: AC1 through AC6 appeared under `## 3. Non-Goals`, while the formal acceptance section contained an empty AC-01 placeholder.
- **Workaround**: Preserved all carried detail and converted the six scenarios into explicit Given/When/Then acceptance criteria before implementation.
- **Suggestion**: Keep carried validation scenarios under a neutral carried-contract section rather than labeling them Non-Goals.

## Diagnostic Details

- **Reproduction**: Read the handed-off spec skeleton and workflow next at specify.
- **Expected / Actual**: Positive scenarios should remain distinct from exclusions; generated placement mixed them.
- **Versions**: Current repository handoff implementation at this unit's starting base.
- **Conditions**: Proposal handoff with a detailed validation section.
- **Workarounds Attempted**: Manual semantic normalization passed unit rules checks.
- **Related Assets**: Proposal handoff skeleton generation; spec-specify guidance.

## Evidence

```text
[STAGE: specify]
[UNMET: not-skeleton(spec.md) not-skeleton(plan.md) not-skeleton(tasks.md)]
Generated spec: ## 3. Non-Goals followed by AC1: Publish a complete ko/en briefing ...
```

## Disposition

- **Disposition (resolved)**: `SPEC-feedback-guidance-fixes` classifies a proposal H2 that mixes non-goals with acceptance, validation or
  verification as a carried contract, placed under `## 5. Carried Proposal Contract` after the acceptance criteria;
  Non-Goals keep their placeholder. Verified by `test_proposal_body.py` and
  `test_mixed_acceptance_and_non_goals_carry_as_contract` in `test_proposal_handoff.py`.
