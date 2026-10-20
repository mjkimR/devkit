---
id: FB-worker-fixtures-inherit-git-context
title: In-worktree pytest fixtures inherit the enclosing Git identity
scope: repo
kind: friction
category: instruction-conflict
target: "development-worker scratch-path contract and packages/devkit-spec/tests/scope Git fixtures"
skill: spec-review
agent: codex
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-20
---

# [FB-worker-fixtures-inherit-git-context] In-worktree pytest fixtures inherit the enclosing Git identity

## 1. Friction

- **Context**: Scope-registry tests ran with pytest basetemp below the assigned worker's ignored cache directory.
- **Expectation**: The worker contract confines scratch files to its worktree; deliberately plain fixture
  directories should still exercise the not-a-Git-worktree branch.
- **Actual**: Three existing tests discovered the enclosing worktree instead: outside-Git CLI error identity,
  locate refusal, and no-op auto-registration assertions failed.
- **Workaround**: Set GIT_CEILING_DIRECTORIES to the ignored fixture parent before running tests. The existing
  assertions then passed without weakening them. Create the basetemp parent first because pytest does not create it.
- **Suggestion**: Document the Git discovery ceiling alongside the in-worktree scratch requirement, or provide a
  fixture-root helper that isolates deliberately non-repository test directories. Keep actual Git fixtures below
  the ceiling so their own repositories remain discoverable.

## Diagnostic Details

- **Reproduction**: Run the scope suite with --basetemp=<worktree>/.pytest_cache/read-access and no Git ceiling.
- **Expected / Actual**: Plain directories raise SPEC_SCOPE_NOT_A_WORKTREE; actual calls inherited the worker's
  registration and returned different errors or a registration warning.
- **Versions**: Python 3.12.8, pytest 9.1.1, macOS Darwin 24.6.0.
- **Conditions**: Ignored scratch is inside an active linked Git worktree; normal pytest /tmp roots do not have this
  enclosing repository.
- **Workarounds Attempted**: GIT_CEILING_DIRECTORIES=<worktree>/.pytest_cache restored 101 passing scope tests;
  the subsequent affected suite with the same ceiling passed 1099 tests.
- **Related Assets**: development-worker role scratch requirement; scope test_cli.py and test_flow.py.

## Evidence

```text
test_outside_git: ARGUMENT_INVALID instead of SPEC_SCOPE_NOT_A_WORKTREE
test_locate_defaults_and_configuration: DID NOT RAISE ScopeNotAWorktreeError
test_auto_register_only_in_a_linked_worktree_at_either_level: unexpected registration warning
After bounded Git discovery: 101 passed; subsequent just test-affected: 1099 passed
```
