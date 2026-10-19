---
id: PLAN-summary-length-guard
spec: SPEC-summary-length-guard
---

# Technical Plan: Summary length guard

## 1. Constitution & Invariant Review

None. The shared validator already runs before writes for all three paths. No dependency or layering change is needed.

## 2. Architecture Overview & Impact

- `packages/devkit-spec/src/devkit_spec/proposals/scaffold.py`: add a 300-character guard to the stripped summary validator shared by proposal, PADR and spec creation; retain `ArgumentError` targeting `--summary`.
- `packages/devkit-spec/tests/proposals/test_proposal_summary.py`: parameterize inclusive boundary and no-write regression tests across library and JSON CLI paths.
- `CAP-DLV-proposal-incubation` and `CAP-DLV-spec-bundles`: state the stripped limit and refusal condition in existing option/error contracts.
- New dependencies: none. Use a fixed creation limit; the existing governance rule's configurable maximum remains independent.

## 3. Error Handling & Edge Cases

Strip once before checking length. Preserve existing empty/non-English validation and omission behavior. The length refusal gives the measured count and an actionable maximum without including the submitted summary. No migration is required.

## 4. Verification & Test Plan

Run the new regression tests before the fix and record their expected assertion failures. Rerun the whole proposal summary module after the fix, then `just lint-check devkit-spec`, `just check devkit-spec`, unit/workflow checks and cumulative rules. The Host runs the full repository suite once on the reviewed final head before integration.

Preparatory timing: characterization, plan and tasks are authored together before the first stage-boundary commit because the known task-coverage gate requires every acceptance criterion to have a task. Stage checks still run in workflow order.
