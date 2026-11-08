---
id: PLAN-adaptive-evidence-repair
spec: SPEC-adaptive-evidence-repair
---

# Technical Plan: `SPEC-adaptive-evidence-repair`

## 1. Constitution & Invariant Review

No change to `ADR-adaptive-development-and-research` or `CAP-DLV-adaptive-development` ownership, authority or verification invariants is needed.

## 2. Architecture Overview & Impact

Extend the existing adaptive-dev guidance and mutable context template. Keep probe selection and classification in evidence-and-iteration, shared failure routing in orchestration, and resume facts in current-context. No runtime, schema or feature edge is added. Reconcile `CAP-DLV-adaptive-development` and `UC-advance-an-idea`.

## 5. Error Handling & Edge Cases

Evidence supports a harness or environment classification; ambiguous cause stays unknown. Failed harness setup never establishes product behavior. Assignment bounds take precedence over the diagnostic fallback. Preserve work and authority in recovery.

## 6. Verification & Test Plan

Review representative walkthroughs for AC-01 through AC-05 with concrete inputs, expected actions, source identity, observed guidance and limits. Run catalog integration packaging checks, relevant asset hygiene, `just lint-check`, `just check`, `just rules-check` and `just test-affected` under repository policy. Packaging does not establish live agent behavior; report live execution separately as unverified if unavailable.
