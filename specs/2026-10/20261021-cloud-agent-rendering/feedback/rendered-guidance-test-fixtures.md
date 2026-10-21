---
id: FB-rendered-guidance-test-fixtures
title: Share rendered bundle fixtures for semantic guidance tests
scope: repo
kind: suggestion
category: redundant-step
target: packages/devkit-spec/tests/
skill: spec-feedback
agent: codex
origin: agent
severity: workaround
recurring: true
status: open
created_at: 2026-10-21
---

# [FB-rendered-guidance-test-fixtures] Share rendered bundle fixtures for semantic guidance tests

## Suggestion

- **Current Procedure**: Semantic guidance checks read source paths directly. Template adoption required equivalent local-render helper functions in role, effort, acceptance and shared-guidance tests.
- **Proposed Procedure**: Provide a shared test support fixture that distinguishes raw package-source assertions from rendered semantic assertions and supports both execution modes.
- **Expected Benefit**: Future conditional guidance changes avoid repeated filename adapters and cannot accidentally omit templated documents from glob-based audits.
- **Cost & Risk**: Test imports and fixture lifetime need care across pytest importlib mode and package-only runs. Preserve existing assertions and raw packaging checks.
- **Attempted**: Local rendered helpers and explicit inventory audits work; a reusable cross-module helper remains unimplemented.

## Diagnostic Details

- **Reproduction**: Convert maintained Markdown to explicit templates, then run focused semantic checks and `just test-affected`.
- **Expected / Actual**: Semantics stay unchanged in local mode; direct source-path reads fail after a rename. A full verification exposed an additional packaging-path assertion after focused tests passed.
- **Versions**: devkit-spec 0.1.0, devkit-dist 0.1.1, Python 3.12.8.
- **Conditions**: pytest importlib mode; explicit .md.jinja sources with final .md destinations.
- **Workarounds Attempted**: Render local content before semantic checks; retain raw source checks for packaging; include both modes in budget/link checks.
- **Related Assets**: test_role_contracts.py, test_effort_procedure.py, test_direct_acceptance_guidance.py, test_bundle_budgets.py, test_package.py.

## Evidence

```text
Focused semantic/rendered checks: 239 passed.
Initial affected full fallback: 1 failed, 4264 passed, 14 skipped.
Failure: test_package.py expected skills/spec/references/backlog.md as a raw source.
```
