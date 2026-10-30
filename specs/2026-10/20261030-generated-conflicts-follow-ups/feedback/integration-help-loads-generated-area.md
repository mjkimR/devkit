---
id: FB-integration-help-loads-generated-area
title: The integration command loads the generated area outside its declared lazy imports
scope: repo
kind: friction
category: other
target: packages/devkit/tests/support/testsupport/layering.py LAZY_IMPORT_AREAS, packages/devkit/src/devkit_agt/features/integration/services/seeding.py
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-30
---

# [FB-integration-help-loads-generated-area] The integration command loads the generated area outside its declared lazy imports

Failing test on main, found by this unit's affected test run.

## 1. Friction / Question (friction, question)

- **Context**: `just test-affected` on this branch after merging `main`.
- **Expectation**: The suite passes; `devkit integration --help` loads only the areas `LAZY_IMPORT_AREAS["integration"]`
  allows (`worktree`).
- **Actual**: `test_mounted_commands.py::test_a_mounted_command_imports_only_its_area_and_lower_layers[integration]`
  fails: the command loads `compact`, `generated`, `integration` and `worktree`. `integration/services/seeding.py`
  imports `devkit_agt.features.generated` at module level since the integrated
  `SPEC-generated-conflicts-in-prepared-merge`. This unit changes none of these paths, and the earlier unit's
  affected run did not select the test, which reads the CLI through a subprocess rather than imports.
- **Workaround (or Interpretation Chosen)**: Left unfixed: the fix (a lazy import in the integration area or a
  deliberate `LAZY_IMPORT_AREAS` entry) is outside this unit's agreed scope; reported to the Host.
- **Suggestion**: Decide whether `integration` may load `generated` (and `compact`) for `--help`: import it lazily in
  `seeding.py`, or add both areas to `LAZY_IMPORT_AREAS["integration"]`; and let an `integration` source change select
  `test_mounted_commands.py`.

## Evidence

```text
E  assert ('integration' in {'compact', 'generated', 'integration', 'worktree'}
     and {...} <= {'integration', 'worktree'})
FAILED packages/devkit/tests/integration/package/test_mounted_commands.py::test_a_mounted_command_imports_only_its_area_and_lower_layers[integration]
just test-affected: 1 failed, 6198 passed, 14 skipped
git diff --name-only <main merge> HEAD -- packages/devkit/src/devkit_agt/features/integration packages/devkit/src/devkit_agt/features/generated packages/devkit/tests/support -> (empty)
seeding.py:14  from devkit_agt.features.generated import classify, load_registry_at   (since 596bca61)
```

## Disposition

Resolved by a session fix on `main`: `integration/services/seeding.py` imports `devkit_agt.features.generated`
inside `GeneratedSeeding.__call__`, so `devkit integration --help` loads only the integration and worktree areas
again, as `LAZY_IMPORT_AREAS` expects. Verified by
`packages/devkit/tests/integration/package/test_mounted_commands.py` and the integration tests.
