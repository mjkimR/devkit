---
id: FB-affected-selection-misses-cross-package-fix-scan
title: Affected-test selection skips the cross-package [FIX] scan for a devkit-spec source change
scope: repo
kind: friction
category: tool-error
target: scripts/affected_tests.py
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-11-11
---

# [FB-affected-selection-misses-cross-package-fix-scan] Affected-test selection skips the cross-package [FIX] scan for a devkit-spec source change

## 1. Friction / Question (friction, question)

- **Context**: A spec unit added a refusal with a `[FIX]` to devkit-spec. The worker and the Host final batch
  checks used `just test-affected --base <sha>`.
- **Expectation**: Affected selection includes every test that reads a changed source file. The guidance says it
  keeps conservative owner dependencies and runs mandatory whole-source-tree checks.
- **Actual**: `packages/devkit/tests/integration/package/test_agent_output_contract.py::test_fixes_carry_no_placeholder`
  scans the `fix=` literals of every package's sources (`source.rglob("*.py")`). It was not selected for the
  devkit-spec change, so a placeholder `[FIX]` landed on main with every final check green. The full suite found it
  later.
- **Workaround (or Interpretation Chosen)**: Ran the test directly, fixed the `[FIX]`, and ran `just test` on main.
- **Suggestion**: Make a source change in any package (not only devkit-dist or devkit-agt) select the
  whole-source-tree contract tests that scan all packages' sources, or declare that test's reads in the selector's
  fixed table.

## Diagnostic Details

- **Reproduction**: Change only `packages/devkit-spec/src/devkit_spec/features/delivery/usecases/specs.py`, then
  run `just test-affected --base main --list` and check whether `test_agent_output_contract.py` is listed.
- **Expected / Actual**: Expected selected; actual not selected. The final batch run at d8e4394a passed
  (5720 passed) while the test failed at that head.
- **Versions**: main d8e4394a; fixed in 19e5fe71.
- **Conditions**: Local-orchestrated batch with three landed units; the devkit-spec change came from unit
  cli-naming-consistency.
- **Workarounds Attempted**: The full `just test` passed after the fix (7117 passed).
- **Related Assets**: `scripts/affected_tests.py`; AGENTS.md Verification; `docs/development/ci-cd.md`.

## Evidence

```text
FAILED packages/devkit/tests/integration/package/test_agent_output_contract.py::test_fixes_carry_no_placeholder
  'packages/devkit-spec/src/devkit_spec/features/delivery/usecases/specs.py:61': 'Pass --task-kind feature|bugfix, ...'
just test-affected --base 2f40fe8c at d8e4394a: mode=partial, 5720 passed (test not selected)
```

- **Disposition**: scripts/affected_tests.py: any package or tool source change now selects `ALL_SOURCES_TESTS` (test_agent_output_contract); verified by test_any_package_source_selects_the_all_sources_scan. The generic docs-path scan is queued as `SPEC-select-tests-by-read-document-paths`.
