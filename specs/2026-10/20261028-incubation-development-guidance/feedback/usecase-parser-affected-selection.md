---
id: FB-usecase-parser-affected-selection
title: Usecase changes omit the repository parser regression from affected tests
scope: repo
kind: friction
category: other
target: scripts/affected_tests.py
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-28
---

# [FB-usecase-parser-affected-selection] Usecase changes omit the repository parser regression from affected tests

## 1. Friction / Question

The friction is a concrete affected-test coverage gap for usecase document syntax.

- **Context**: A new usecase and catalog consumer test were added during incubation guidance Development.
- **Expectation**: Relevant document parser regressions should be selected for changed files under `docs/usecases/`.
- **Actual**: `just test-affected --base 86263d6e` selected the catalog e2e and five document/code test files, but omitted `packages/devkit-docs/tests/integration/features/governance/test_ux_repository_usecases.py`. The new usecase used a human-readable bold extension label that its parser did not recognize.
- **Workaround**: Ran the omitted regression explicitly, observed its failure on the new usecase, corrected the marker to the template form `- **2a.** Label: ...`, and reran it successfully.
- **Suggestion**: Include the repository-usecase parser regression when usecase documents change; retain the existing full fallback and avoid selecting unrelated test areas.

## Diagnostic Details

- **Reproduction**: In `<worktree>`, add/change a usecase extension marker, then run `just test-affected --base <accepted-head>` and inspect its selected paths. Run the omitted test explicitly for comparison.
- **Expected / Actual**: Parser coverage for changed usecase structure / no repository-parser test in the six selected paths; the explicit regression found an unparsed extension.
- **Versions**: devkit 0.1.4; accepted comparison head `86263d6e55a87fcb834b24828249bdcc7d462a3d`.
- **Conditions**: A new `docs/usecases/delivery/UC-incubate-an-idea.md` plus catalog e2e/spec evidence changes; partial mode selected with reason `docs/,tests`.
- **Workarounds Attempted**: Explicit parser regression failed once before the marker correction and passed once afterward. The selector was not edited inside this task.
- **Related Assets**: `scripts/affected_tests.py`, the usecase template, and `packages/devkit-docs/tests/integration/features/governance/test_ux_repository_usecases.py`.

## Evidence

```text
just test-affected --base 86263d6e
[TEST_SELECTION: mode=partial ... changed=12 paths=6 reason=docs/,tests]
Selected catalog e2e, docs/spec/agt documented-code tests, agt docs rules and workflow library tests.
The repository-usecase parser regression was absent.

Explicit parser regression before correction:
AssertionError: docs/usecases/delivery/UC-incubate-an-idea.md
assert any(step.extension for step in parsed.steps)
1 failed

After correcting '- **2a. Label**:' to '- **2a.** Label:':
1 passed
```

## Disposition

Resolved by the session change to `scripts/affected_tests.py`: changes under `docs/usecases/`, including deleted
files, select `test_ux_repository_usecases.py` in addition to the existing document checks.
The regression in `packages/devkit/tests/e2e/package/test_affected_tests.py` covers existing and deleted usecases
and the unrelated `docs/usecases-other/` prefix. The existing full fallback is preserved.

Verification: the focused Red run reproduced the failures before the fixes; both changed regression files passed
90 tests after the fixes. The cumulative affected selection passed 1,573 tests. Ruff, Pyright, governance rules,
and `devkit sync --check` passed. Independent code review of commit `2664c8c6c9d5d27e3fd247949b8f6d21d91ad9ab`
reported no findings; the Host verified the reviewed tree was unchanged.
