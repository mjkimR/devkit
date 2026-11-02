---
id: FB-docs-wheel-rule-count-stale
title: The document-only wheel test still expects nine docs rules
scope: repo
kind: friction
category: docs-mismatch
target: packages/devkit-docs/tests/e2e/bundles/docs/test_installed_consumer.py
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-11-02
---

# [FB-docs-wheel-rule-count-stale] The document-only wheel test still expects nine docs rules

## 1. Friction / Question (friction, question)

- **Context**: A change to `packages/devkit-mcp/pyproject.toml` made `just test-affected` select the full suite.
- **Expectation**: The full suite passes on `main`.
- **Actual**: `test_document_only_built_wheels` fails with `assert 10 == 9`. The docs bundle has shipped ten rules
  since `decision_supersession` was added (`2510282d`, 2026-10-31), but the test still counts nine. The test fails the
  same way on `main`.
- **Workaround (or Interpretation Chosen)**: The failure was left as is, because it is outside the scope of
  `SPEC-retire-stale-integration-clauses`.
- **Suggestion**: Update the expected count, or derive it from the bundle's registered rules so that a new rule does
  not break the test.

## Diagnostic Details

- **Reproduction**: `uv run pytest packages/devkit-docs/tests/e2e/bundles/docs/test_installed_consumer.py::test_document_only_built_wheels`
- **Expected / Actual**: Expected a pass; observed `AssertionError: assert 10 == 9` at line 46.
- **Versions**: `main` at `400653a4`.
- **Conditions**: An e2e test that runs only in full-suite selections and nightly CI.
- **Workarounds Attempted**: none.
- **Related Assets**: `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/` (ten rule directories).

## Evidence

```text
FAILED packages/devkit-docs/tests/e2e/bundles/docs/test_installed_consumer.py::test_document_only_built_wheels
E       AssertionError: assert 10 == 9
```
