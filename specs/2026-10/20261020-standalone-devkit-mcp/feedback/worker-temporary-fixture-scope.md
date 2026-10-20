---
id: FB-worker-temporary-fixture-scope
title: Clarify isolated test temporary directories for confined workers
scope: repo
kind: friction
category: instruction-conflict
target: packages/devkit-spec/src/devkit_spec/bundle/subagents/development-worker.md
skill: spec-review
agent: codex
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-20
---

# [FB-worker-temporary-fixture-scope] Clarify isolated test temporary directories for confined workers

## 1. Friction

- **Context**: A confined Development worker ran required full-fallback and dist-only checks.
- **Expectation**: Fixture placement should preserve both worker write boundaries and tests of non-Git directories.
- **Actual**: The role says temporary fixtures belong in pytest tmp_path or an ignored worktree path, then says never outside it. Interpreting the final phrase as the worktree forced basetemp beneath a Git checkout. Existing core fixtures remove inherited GIT variables, so even a ceiling override did not consistently isolate discovery.
- **Workaround**: The Host explicitly allowed pytest-managed system temporary roots. Isolated HOME, settings and logs remained there. Passing basetemp on the parent command line avoided leaking it into nested pytest processes.
- **Suggestion**: State whether pytest-owned isolated system temporary directories are already authorized, and distinguish them from authored scratch. Recommend command-line basetemp rather than PYTEST_ADDOPTS for suites that invoke pytest recursively.

## Diagnostic Details

- **Reproduction**: Run dist-only tests with basetemp under an ignored worktree directory, then add GIT_CEILING_DIRECTORIES; core tests still remove the ceiling. Run the full suite with PYTEST_ADDOPTS basetemp; nested rule tests reject a parent-of-cwd temporary root.
- **Expected / Actual**: Expected independent temporary projects; observed inherited Git roots and nested pytest argument refusals.
- **Versions**: Python 3.12.8, pytest 9.1.1.
- **Conditions**: Emulated confinement; sibling worktree writes need command-scoped permission.
- **Workarounds Attempted**: Internal basetemp: 295 dist failures. Ceiling override: 16 failures, mostly inherited Git discovery. Authorized external fixtures and command-line basetemp: full suite 3884 passed, 14 skipped.
- **Related Assets**: Development worker contract; scripts/module.sh; packages/devkit-dist/tests/core/conftest.py.

## Evidence

```text
--workspace-root is inside the Git work tree; the devkit root is the repository top level
argument --basetemp: basetemp must not be ... any parent directory of [cwd]
TEST_SELECTION: mode=full reason=packages/devkit-dist/pyproject.toml
3884 passed, 14 skipped
```

## Disposition

Resolved directly in a session change to
`packages/devkit-spec/src/devkit_spec/bundle/subagents/development-worker.md` and
`packages/devkit-spec/tests/test_role_contracts.py`. Authored scratch stays inside the worktree; pytest-managed
isolated system temporary fixtures are explicitly allowed outside it, subject to sandbox permissions. Both the
procedure and denied-path list name the exception. Recursive pytest runs pass custom `--basetemp` through the
parent command line instead of `PYTEST_ADDOPTS`.

Verification: `just test-affected --base main` passed 1,140 tests; `just lint-check spec` passed; `just check spec`
reported zero errors and warnings. Low-effort self-review checked the exception against the unchanged caller-checkout
and sandbox restrictions. The existing scratch-file contract in `CAP-DLV-delivery-workflows` is unchanged; this
clarifies pytest fixture placement in the worker instructions. No test runner or fixture implementation change was
needed, and this session does not claim a new full-suite reproduction of the historical failures.
