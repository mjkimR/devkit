---
id: PADR-informational-range-inspection-reuses-existing-checks
title: Informational range inspection reuses existing checks
summary: The range inspection command reports each existing worker-result check as pass, fail or not-run with its existing codes, exits 0, 1 or 2 by the agent output convention, and blocks, writes or repairs nothing.
proposal: PROP-worker-range-validation
status: draft
created_at: 2026-10-20
---

# [PADR-informational-range-inspection-reuses-existing-checks] Informational range inspection reuses existing checks

- **Status**: Draft
- **Date**: 2026-10-20

---

## 1. Context & Problem Statement

The Host validates every returned worker range by hand (`spec-delegate` `references/worker.md`): ancestry from the
last accepted head, changed paths against the write scope, a clean worktree, envelope validity, the cumulative rules
check and `devkit workflow next`. Each check already exists as a Git command or a devkit command; what is missing is
one invocation that runs them over an explicit range and returns one result, including the compared heads and
changed paths a read-only reviewer needs (`FB-reconcile-reviewer-no-diff-list`).

## 2. Decision Drivers

- Agent-first output (`ARCH-08-1-agent-output`): one JSON object or sentinel lines, stable codes, `0`/`1`/`2` exits.
- No new gate, approval, registration or override (plan-intent): findings are evidence for the main agent.
- Reuse, not reimplementation: existing codes and actions of the wrapped checks are preserved.

## 3. Considered Options

1. A thin command in `devkit-spec` that calls the existing checks and aggregates their results (chosen).
2. A new check class in the workflow engine evaluated at a stage's exit: rejected, it would become a gate.
3. Documentation-only (a shell recipe in `spec-delegate`): rejected, the hand-written scope pattern stays per run and
   the reviewer payload still lacks a generated path list.

## 4. Decision Outcome

- Inputs are explicit: the unit directory, the last accepted head (`--base`), the returned head (`--head`) and the
  write scope the Host passed the worker. The command derives no base, head or scope by itself.
- Each check reports `pass`, `fail` or `not-run` (with its cause), so a check that could not run is distinct from a
  negative result. The checks: ancestry of base to head; worktree HEAD equals `--head`; changed paths of
  `git diff --name-only <base> <head>` with those outside the scope; worktree status; `devkit workflow envelope check`
  results (malformed files, `blocked`, `pending_questions`); the cumulative rules check over the range (the
  `devkit rules check --ci --base <base>` evaluation, run only when the worktree HEAD equals `--head`, otherwise
  `not-run`); and the stage `devkit workflow next` names.
- Exit codes follow the convention: `0` every check passed, `1` at least one check failed (a negative result, not a
  refusal), `2` the command could not run (bad arguments, not a Git worktree, unknown refs). A `not-run` check alone
  does not make the exit `1`; it is reported as a notice.
- Structured output (`--format json`) is one object with the compared `base` and `head`, `changed_paths`,
  `outside_scope` and the per-check results; this object, or its `base`, `head` and `changed_paths`, is what the Host
  passes a read-only reviewer.
- The command modifies no file, writes no record, runs no `devkit sync`, merges nothing, retries nothing and enlarges
  no scope. Whether a finding blocks the worker's result stays the Host's decision under the existing
  `spec-delegate` procedure.

## 5. Consequences

- The Host's per-range validation becomes one call; its decision and recording (accept, or block with a `worker`
  envelope) are unchanged.
- Reviewer payloads can carry a generated changed-path list instead of the caller's selection.
- The rules check over the range is as costly as `devkit rules check --ci`; the command runs it once per call.
