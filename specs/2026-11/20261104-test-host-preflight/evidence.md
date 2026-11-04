# Verification evidence

## Controlled baseline comparison

Loaded the input script with `git show e91c47ba2f8cd90083186b47f5295791912f84b6:scripts/check_test_environment.py`
and the changed script with `runpy`, without checking out the base. In both, injected a working socketpair and a
TCP socket constructor raising `PermissionError(EPERM)`, then invoked `-- just test all` through Click's runner.

```text
baseline: exit=0 loopback_advisory=False
current: exit=2 loopback_advisory=True
```

## Automated checks

- Focused preflight and module script integration tests: 56 passed, including live permitted bind and injected
  create/bind/listen denials, retry quoting, socket closure, safe selection and recipe stop-before-pytest.
- Existing affected-selector e2e tests: 80 passed during the initial combined run. That run also exposed one
  newly added recipe-test expectation for a nonexistent viewer unit directory; corrected it to the actual module
  selector inventory, then reran the focused tests successfully.
- `just test-affected --base e91c47ba2f8cd90083186b47f5295791912f84b6`: partial selection, 8 paths, 71 passed.
- Ruff lint and format: passed on the changed Python files.
- `uv run pyright scripts/check_test_environment.py`: zero errors, warnings or information messages.
- `bash -n scripts/module.sh` and `git diff --check`: passed.

Tests ran with the operation-specific host permission needed for sibling-worktree caches and local socket use.
The initial sandboxed Ruff attempt could not write its cache; the approved rerun passed. No tests were skipped or
weakened. No external connectivity probe or wheel-build download was performed for this change.
