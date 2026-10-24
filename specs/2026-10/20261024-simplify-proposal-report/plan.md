---
id: PLAN-simplify-proposal-report
spec: SPEC-simplify-proposal-report
---

# Technical Plan: `SPEC-simplify-proposal-report` Simplify proposal review report template

## 1. Architecture Overview & Impact
- Target Area: `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/report.py`
- Tests: `packages/devkit-spec/tests/integration/features/proposals/test_proposal_report.py`
- Downstream usages: `packages/devkit-spec/src/devkit_spec/features/delivery/usecases/native_plan_accept.py` (via `planning_support()`)

## 2. Component Breakdown & Interface Contracts

### 2.1 `report.py` Constants & Checks
- Update `SECTIONS`:
  - `en`: `("Outcome", "Decisions", "Proposed approval effects")`
  - `ko`: `("결론", "결정", "제안된 승인 효과")`
- Update `DECISION_FIELDS`:
  - `en`: `("Problem", "Choice")`
  - `ko`: `("문제", "선택")`
- Update `_check()`:
  - Validate the 3 mandatory H2 sections.
  - In `Decisions`, ensure all committed PADRs exist as H3 sections, and each contains `Problem` and `Choice` (either as H4 headers or inline labeled fields).
  - In `Proposed approval effects`, verify that `selected.dev_effort` is present.
  - Remove mandatory envelope filename checks (`selected.coverage`) so arbitrary envelope listings are no longer required to pass.
- Update `template()`:
  - Render the 3 H2 sections.
  - Render each PADR with `Problem` and `Choice` placeholders.
  - Include `selected.dev_effort` in `Proposed approval effects`.
- Update `planning_support()`:
  - If an optional `Planning effort and support` (or `Planning 노력 및 지원`) section exists in the report, return it.
  - Otherwise, return a default string derived from frontmatter/selected metadata (e.g. `f"effort={selected.effort}"` or summary from effects) to prevent index errors.

### 2.2 Integration Tests
- Update `test_proposal_report.py` fixtures and assertions to reflect the streamlined 3-section format and compact PADR fields.
- Verify both English (`en`) and Korean (`ko`) generation, publication and validation.
- Verify that omitting optional sections does not trigger `ReportInvalidError`.

## 3. Verification & Test Plan
- Run `just test devkit-spec test_proposal_report`
- Run `just test-affected`
- Run `just lint devkit-spec` and `just check devkit-spec`
