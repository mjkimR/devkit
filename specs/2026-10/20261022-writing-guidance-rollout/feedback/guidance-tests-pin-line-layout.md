---
id: FB-guidance-tests-pin-line-layout
title: Some bundle guidance tests match phrases on raw lines, so rewrapping text breaks them
scope: repo
kind: friction
category: other
target: packages/devkit-spec/tests/integration/bundles/spec/
skill: none
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-22
---

# [FB-guidance-tests-pin-line-layout] Some bundle guidance tests match phrases on raw lines, so rewrapping text breaks them

Test brittleness: assertions depend on line wrapping, not on wording.

## 1. Friction / Question (friction, question)

- **Context**: Rewriting bundle skills and role contracts under `agent-asset-writing` (`SPEC-writing-guidance-rollout`).
- **Expectation**: A test that pins a phrase passes as long as the phrase's words and order stay, as in the tests that
  normalize whitespace with `" ".join(text.split())`.
- **Actual**: `test_unit_dependency_guidance`, `test_milestone_completion_guidance` and parts of `test_role_contracts`
  search the raw file text, so a phrase split across two lines by rewrapping fails the test although its wording is
  unchanged. Rewriters had to keep asserted phrases on one line and rewrap twice in one file.
- **Workaround (or Interpretation Chosen)**: Kept each asserted phrase on a single raw line.
- **Suggestion**: Normalize whitespace in these tests (one shared helper in the bundle test support), so assertions
  pin wording, not layout.

## Diagnostic Details

- **Reproduction**: Rewrap a sentence of `skills/spec/references/backlog.md.jinja` that contains "only when the
  prerequisite is explicitly waived" across two lines; `test_pickup_order_and_lifecycle_guards` fails.
- **Expected / Actual**: Expected pass for unchanged wording; actual failure on the line break.
- **Versions**: devkit-spec at base `e52ed6e6`.
- **Conditions**: Any rewrap of bundle prose pinned by these tests.
- **Workarounds Attempted**: Single-line phrases; tests then pass.
- **Related Assets**: `packages/devkit-spec/tests/integration/bundles/spec/test_unit_dependency_guidance.py`,
  `test_milestone_completion_guidance.py`, `test_role_contracts.py`.

## Evidence

```text
Rewriter reports: "the test checks raw text without whitespace normalization, so I kept every asserted clause on a
single line"; failures cleared after rejoining the phrase onto one line.
```
