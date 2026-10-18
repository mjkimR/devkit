---
id: FB-fresh-worktree-environment-bootstrap
title: Fresh worktree has synchronized assets but no runnable project environment
scope: repo
kind: friction
category: tool-error
target: devkit worktree start and spec worktree procedure
skill: spec
agent: codex
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-18
---

# [FB-fresh-worktree-environment-bootstrap] Fresh worktree has synchronized assets but no runnable project environment

## 1. Friction

- **Context**: Started a required task worktree for a catalog content deletion.
- **Expectation**: The printed worktree destination supports the prescribed devkit spec commands.
- **Actual**: Start reported synced=yes with setup=-, but uv run --no-sync devkit created an empty virtual environment
  and failed to spawn devkit. A normal uv run in the restricted base checkout also tried resolving the released model
  dependency before a read-only context command could run.
- **Workaround**: Invoked the base checkout's installed devkit executable with the worktree as current directory, then
  linked the worktree virtual environment to the existing base environment for checks. Source packaging was verified
  independently through built wheels in the fresh consumer smoke test.
- **Suggestion**: Document how to provision or reuse an environment before the first post-start command when no setup
  command is configured. Asset synchronization alone does not establish a runnable uv project environment.

## Diagnostic Details

- **Reproduction**: Start a new task worktree with no setup command, change directory, run uv run --no-sync devkit spec new.
- **Expected / Actual**: Expected installed CLI; observed an empty environment and executable-not-found failure.
- **Versions**: devkit-agt 0.1.1, devkit-spec 0.1.0; Python 3.12.3.
- **Conditions**: Existing base virtual environment; new linked checkout; worktree=required; setup unset.
- **Workarounds Attempted**: Base executable worked; shared virtual environment restored package type resolution.
- **Related Assets**: .agents/skills/spec/references/worktree.md; scripts/module.sh.

## Evidence

```text
worktree start: created=yes setup=- synced=yes
uv run --no-sync devkit: Creating virtual environment at .venv; Failed to spawn devkit; No such file or directory.
Type check with empty worktree environment: Import pytest could not be resolved.
Type check with reused base environment: 0 errors, 0 warnings, 0 informations.
```
