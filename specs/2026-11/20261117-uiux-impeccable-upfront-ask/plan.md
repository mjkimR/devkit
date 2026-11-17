---
id: PLAN-uiux-impeccable-upfront-ask
spec: SPEC-uiux-impeccable-upfront-ask
---

# Technical Plan: `SPEC-uiux-impeccable-upfront-ask` Ask about Impeccable at the start of app-uiux-improve

## 1. Architecture Overview & Impact

- Target Area: the `app-uiux-improve` bundle in `devkit-catalog` (content only) and its Living Spec.
- No code, feature edge, package boundary or runtime changes; ARCH documents are unaffected.
- Decision: new `ADR-impeccable-upfront-ask` supersedes in part `ADR-impeccable-session-authority` (the clause that an
  installed Impeccable permits an offer). Selection-before-use stays in force.
- Design, domain and operations impact: none; the change is instruction text for an opt-in bundle.

## 2. Component Breakdown & Interface Contracts

- `skills/app-uiux-improve/SKILL.md`: Boundaries line replaces "permits an offer" with the upfront question;
  Procedure step 1 asks the Impeccable question in the first round unless the request already decides; step 4
  follows the answer.
- `references/orchestration.md` "Select and set up" step 1: same contract, availability stated in the question.
- Bundle `README.md`: usage and "what it does not do" describe the question.
- `CAP-DLV-uiux-improvement` rule 15: adds the WHERE/WHEN clause for the upfront question (MUST), citing the new ADR.
- `UC-improve-an-interface-and-user-flow`: step 1 recovers or asks the Impeccable choice; extension 3c refers to it.
- Tests: `test_impeccable_delegation_is_selected_briefed_routed_and_accepted` asserts the new phrases.

## 3. Verification & Test Plan

- `uv run pytest packages/devkit-catalog/tests/integration/bundles/test_app_uiux_improve.py`
- `just test-affected`, `uv run devkit rules check`, lint/type checks via the repository recipes.
- Self-containment: `rg -n '\b(ADR|PADR|CAP|UC|UX|ARCH|SPEC|PROP|MS|MAT|FB)-[A-Za-z0-9]'` over the bundle.
