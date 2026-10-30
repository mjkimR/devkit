---
id: FB-envelope-commit-fix-placeholder-fails-output-contract
title: Envelope commit fix text fails the agent output contract test on the base
scope: repo
kind: friction
category: tool-error
target: packages/devkit/src/devkit_agt/features/workflow/services/envelope/commit.py
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-30
---

# [FB-envelope-commit-fix-placeholder-fails-output-contract] Envelope commit fix text fails the agent output contract test on the base

## 1. Friction / Question (friction, question)

- **Context**: Development of `SPEC-deep-research-bundle`; `just test-affected` selected the full suite because
  `packages/devkit-catalog/pyproject.toml` changed.
- **Expectation**: The base passes the full suite, so a full selection reports only failures the change caused.
- **Actual**: `packages/devkit/tests/integration/package/test_agent_output_contract.py::test_fixes_carry_no_placeholder`
  fails on the `fix` of `EnvelopeCommitInvalidError` in `commit.py:17`, which names `SPEC-<slug> or PROP-<slug>` as a
  placeholder. Neither file is in this Unit's diff; `commit.py` last changed in `8ef6543b`, already on the base.
- **Workaround (or Interpretation Chosen)**: Reported the failure as pre-existing and unrelated in the review and
  final report; the file is outside this Unit's write scope.
- **Suggestion**: Make the fix name the exact command that lists valid anchors, or a concrete action without a
  placeholder, and keep the full suite green on the base.

## Diagnostic Details

- **Reproduction**: `just test-affected` (mode=full) or `just test devkit tests/integration/package/test_agent_output_contract.py`.
- **Expected / Actual**: Expected pass; actual `AssertionError: a [FIX] is the exact command or edit`.
- **Versions**: devkit 0.1.5 at the Unit's base `a6927bf9`.
- **Conditions**: Any change that selects the full suite.
- **Workarounds Attempted**: none beyond reporting.
- **Related Assets**: `commit_message` in `commit.py`; `test_fixes_carry_no_placeholder`.

## Evidence

```text
FAILED packages/devkit/tests/integration/package/test_agent_output_contract.py::test_fixes_carry_no_placeholder
{'packages/devkit/src/devkit_agt/features/workflow/services/envelope/commit.py:17': 'Use a tracked SPEC-<slug> or ...'}
1 failed, 6067 passed, 14 skipped
```

## Disposition

Resolved by `SPEC-lifecycle-feedback-fixes` (AC-01): the unsupported-anchor fix of `EnvelopeCommitInvalidError`
in `commit.py` is now a concrete action (commit the `[TARGET]` envelope with a manual `git commit`) without a
placeholder. Verified: the base fix matched the contract test's placeholder pattern and the head fix does not;
`test_fixes_carry_no_placeholder`, `test_class_fixes_carry_no_placeholder` and `test_unsupported_anchor_ids_refuse`
pass, and `packages/devkit/tests/integration/package` passes (163 tests).
