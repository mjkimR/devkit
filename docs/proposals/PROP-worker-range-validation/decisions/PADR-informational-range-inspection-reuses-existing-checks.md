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

1. A thin command in `devkit-spec` that calls the existing checks and aggregates their results (chosen), named
   `devkit spec worker inspect`; `devkit spec range inspect` and `devkit spec scope inspect` (mixing it with the
   scope registry) were the alternatives.
2. A new check class in the workflow engine evaluated at a stage's exit: rejected, it would become a gate.
3. Documentation-only (a shell recipe in `spec-delegate`): rejected, the hand-written scope pattern stays per run and
   the reviewer payload still lacks a generated path list.

## 4. Decision Outcome

- The command is `devkit spec worker inspect [--unit <dir>] --base <accepted> --head <returned>
  [--scope <prefix>... | --scope-file <path>] [--base-checkout <path>]`, in a new small `worker` group of
  `devkit spec`.
- Inputs: the last accepted head (`--base`) and the returned head (`--head`) are required, because only the Host
  knows the last accepted head and the HEAD-equals-returned-head check needs an explicit returned head; the write
  scope the Host passed the worker in the payload's `allowed_boundaries` is optional (`--scope`, repeatable
  directory or path prefixes, or `--scope-file`). The command derives no base, head or scope by itself and never
  falls back to the scope registry (`devkit spec scope`), whose declared spec paths differ from a worker's write
  scope.
- The unit is optional (user decision at the `plan-accept` review). An explicit `--unit` wins. Without it the
  command infers the unit from the branch/unit binding devkit-spec already uses for the worktree's activity branch:
  the `branch.<branch>.devkitUnit` marker `devkit worktree start --existing-branch --unit` records, else the
  activity-branch correspondence of the `devkit.attach_check` extension (`plan-<slug>` to
  `docs/proposals/PROP-<slug>`; `dev-<slug>` to its spec bundle `specs/<YYYY-MM>/<YYYYMMDD>-<slug>`, or before the
  handoff the proposal bundle `docs/proposals/PROP-<slug>`). A detached HEAD, a branch that is not an activity
  branch, or no or more than one matching unit directory means the command could not run: exit `2` with a stable
  code (such as `WORKER_UNIT_UNRESOLVED`) whose action is to pass `--unit`. The result names the unit used and
  whether it was given or inferred.
- Each check reports `pass`, `fail` or `not-run` (with its cause), so a check that could not run is distinct from a
  negative result. The checks: ancestry of base to head; worktree HEAD equals `--head`; changed paths of
  `git diff --name-only <base> <head>` with those outside the scope (`not-run` when no scope was given, leaving the
  judgment to the Host); worktree status; `devkit workflow envelope check`
  results (malformed files, `blocked`, `pending_questions`); the cumulative rules check over the range (the
  `devkit rules check --ci --base <base>` evaluation, run only when the worktree HEAD equals `--head`, otherwise
  `not-run`); and the stage `devkit workflow next` names. With `--base-checkout <path>` the result also carries
  that checkout's HEAD and dirty paths as information, not as a check: comparing them with what the Host recorded
  before spawning stays the Host's step.
- Exit codes follow the convention: `0` every check passed, `1` at least one check failed (a negative result, not a
  refusal), `2` the command could not run (bad arguments, not a Git worktree, unknown refs, no unit given or
  inferable). A `not-run` check alone
  does not make the exit `1`; it is reported as a notice.
- Structured output (`--format json`) is one object with the `unit` (and whether it was given or inferred), the
  compared `base` and `head`, `changed_paths`,
  `outside_scope` (absent when no scope was given), `base_checkout` (its `head` and `dirty_paths`, only with
  `--base-checkout`) and the per-check results; this object, or its `base`, `head` and `changed_paths`, is what the Host
  passes a read-only reviewer.
- The command modifies no file, writes no record, runs no `devkit sync`, merges nothing, retries nothing and enlarges
  no scope. Whether a finding blocks the worker's result stays the Host's decision under the existing
  `spec-delegate` procedure.

## 5. Consequences

- The Host's per-range validation becomes one call; its decision and recording (accept, or block with a `worker`
  envelope) are unchanged.
- Reviewer payloads can carry a generated changed-path list instead of the caller's selection.
- The rules check over the range is as costly as `devkit rules check --ci`; the command runs it once per call.
