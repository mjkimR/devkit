---
id: ADR-keep-uv-run-as-the-agent-facing-devkit-invocation
title: Keep uv run as the agent-facing devkit invocation
summary: "For agent guidance that calls devkit, we keep uv run devkit as the documented form, to run the locked devkit from any directory and sync it after a lock change, accepting about 10-20 ms per call."
status: accepted
created_at: 2026-10-22
---

# [ADR-keep-uv-run-as-the-agent-facing-devkit-invocation] Keep uv run as the agent-facing devkit invocation

- **Status**: Accepted
- **Date**: 2026-10-22
- **Deciders**: the user, on the rejection of ~~`PROP-direct-devkit-invocation`~~ (Git `4672a101eec0`)
- **Involved Components/Capabilities**: `capabilities/harness/`, `capabilities/distribution/`

---

## 1. Context & Problem Statement

Agent guidance tells agents to call `uv run devkit ...`: the managed `AGENTS.md` block, the generated
`devkit-workflow` entry skill and several bundle instructions. `uv run` verifies, and when needed synchronizes, the
project environment before each call; measured, it costs about 18-23 ms over the project's `.venv/bin/devkit` on
commands that take 120-450 ms. Hooks already avoid it: commit gates run the worktree's `.venv` interpreter and Codex
host hooks run `devkit` from `PATH`. The guidance is committed and shared by every consumer repository, host and
clone, so any form it names must work from any working directory and must not run a devkit older than the lock.
devkit targets POSIX only (`ARCH-03-context`).

## 2. Decision Drivers

- Correctness: the called devkit matches the committed `uv.lock` after `git pull`, a branch switch or a new worktree.
- Portability: the form works from any directory of any consumer repository on Claude Code, Codex and Antigravity,
  without machine-specific paths in committed files.
- Failure: a missing environment ends in an instruction the agent can act on.
- Cost: the per-call overhead on frequent paths.

## 3. Considered Options

- **Keep `uv run devkit`** (current): locked, synced and directory-independent; costs about 20 ms per call.
- **`uv run --no-sync devkit`**: directory-independent, saves about 9-14 ms; silently runs an older devkit after a
  lock change and creates an empty `.venv` when none exists.
- **`.venv/bin/devkit`** on frequent paths: saves about 18-23 ms; fails with exit 127 from any subdirectory or without
  an environment, and silently runs an older devkit after a lock change.
- **Activated environment (bare `devkit`)**: no overhead; depends on each host's shell state, which can point at
  another project's environment.
- **Executable path recorded at sync**: no overhead; machine-specific, so it cannot appear in the committed
  `AGENTS.md` block, and it goes stale the same way.

## 4. Decision Outcome

Keep `uv run devkit` as the documented agent-facing form on every path.

- It is the only option that meets the correctness and portability drivers; every direct form trades them for a
  saving of 2-14 % of a frequent call, about 1 s across a 50-call agent session.
- Hooks keep their current forms; they never paid the `uv run` cost.

## 5. Consequences

- Positive: no consumer-facing change; guidance keeps one form that behaves the same in every repository and host.
- Negative: each agent call keeps the 10-20 ms `uv run` overhead.
- Follow-up: if a measured agent session shows `uv run` overhead above 5 % of its devkit wall time, revisit with that
  measurement.

## 6. Confirmation

Review only: the measurements and failure probes in the rejected proposal's `materials/invocation-forms.md` (Git `4672a101eec0`). A draft proposal that changes the documented invocation form cites a new measurement against this decision's follow-up threshold.
