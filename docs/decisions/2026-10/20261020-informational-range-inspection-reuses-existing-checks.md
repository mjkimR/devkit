---
id: ADR-informational-range-inspection-reuses-existing-checks
title: Informational range inspection reuses existing checks
summary: The range inspection command derives its unit, range, write scope and base checkout from the worktree and the unit's committed records (flags override), reports each existing worker-result check as pass, fail or not-run with its existing codes, exits 0, 1 or 2, and blocks, writes or repairs nothing.
proposal: SPEC-worker-range-validation
status: accepted
created_at: 2026-10-20
---

# [ADR-informational-range-inspection-reuses-existing-checks] Informational range inspection reuses existing checks

- **Status**: Accepted
- **Date**: 2026-10-20

---

## 1. Context & Problem Statement

The Host validates every returned worker range by hand (`spec-delegate` `references/worker.md`): ancestry from the
last accepted head, changed paths against the write scope, a clean worktree, envelope validity, the cumulative rules
check and `devkit workflow next`. Each check already exists as a Git command or a devkit command; what is missing is
one invocation that runs them over the unit's range and returns one result, including the compared heads and
changed paths a read-only reviewer needs (`FB-reconcile-reviewer-no-diff-list`). The inputs the Host supplies by hand
(unit, last accepted head, returned head, write scope, base checkout) are already determined by the worktree and the
unit's committed records, so the command derives them.

## 2. Decision Drivers

- Agent-first output (`ARCH-08-1-agent-output`): one JSON object or sentinel lines, stable codes, `0`/`1`/`2` exits.
- No new gate, approval, registration or override (plan-intent): findings are evidence for the main agent.
- Reuse, not reimplementation: existing codes and actions of the wrapped checks are preserved.
- Derive, never guess: an input the records do not determine is a could-not-run with a stable code, and an explicit
  flag only overrides a derived value (user decision at the `plan-accept` review).

## 3. Considered Options

1. A thin command in `devkit-spec` that derives its inputs, calls the existing checks and aggregates their results
   (chosen; the explicit-input variant was superseded at the `plan-accept` review), named
   `devkit spec worker inspect`; `devkit spec range inspect` and `devkit spec scope inspect` (mixing it with the
   scope registry) were the alternatives.
2. A new check class in the workflow engine evaluated at a stage's exit: rejected, it would become a gate.
3. Documentation-only (a shell recipe in `spec-delegate`): rejected, the hand-written scope pattern stays per run and
   the reviewer payload still lacks a generated path list.

## 4. Decision Outcome

- The command is `devkit spec worker inspect [--unit <dir>] [--base <accepted>] [--head <returned>]
  [--scope <prefix>... | --scope-file <path>] [--base-checkout <path>]`, in a new small `worker` group of
  `devkit spec`, run in the unit's worktree. Every input is derived as below; a flag replaces only its own input.
  The unit's records are read as committed at the worktree HEAD; uncommitted files are never read as records.
- **Unit**: `--unit`, else the unit bound to the worktree's activity branch: the `branch.<branch>.devkitUnit` marker
  `devkit worktree start --existing-branch --unit` records, else the activity-branch correspondence of the
  `devkit.attach_check` extension (`plan-<slug>` to `docs/proposals/PROP-<slug>`; `dev-<slug>` to its spec bundle
  `specs/<YYYY-MM>/<YYYYMMDD>-<slug>`, or before the handoff the proposal bundle `docs/proposals/PROP-<slug>`). A
  detached HEAD, a branch that is not an activity branch, or no or more than one matching unit directory:
  `WORKER_UNIT_UNRESOLVED`.
- **Returned head**: `--head`, else the commit that added the unit's latest `worker` envelope (the highest
  `envelopes/worker-NN.yaml`), found with `git log --diff-filter=A` on that file. No `worker` envelope, or a file
  that more than one commit added: `WORKER_HEAD_UNRESOLVED`.
- **Base** (the last accepted head): `--base`, else from the previous `worker` envelope (the next-highest number) and
  the unit's state at the commit that added it, `P`, which is the state the latest run was spawned from:
  - not blocked at `P` (no problem without a resolution among the records at `P`): the base is `P`;
  - blocked at `P`: the `diff_scope.base` that the unresolved problem envelopes at `P` record (the Host's blocking
    `worker` envelope records its `--base`; a failed worker's records the base it was given), so the blocked range
    keeps its start and a Host fix or resolution committed since stays inside the range;
  - no previous `worker` envelope: the merge base of the worktree HEAD with the base branch, which is the branch's
    `devkitBase` marker or else the base checkout's current branch.
  Unresolved problem envelopes that record no `diff_scope.base` or different ones, a base checkout that is detached
  or on the activity branch itself with no `devkitBase`, or no single merge base: `WORKER_BASE_UNRESOLVED`. The
  latest envelope's own state (a problem it records now) does not move the base.
- **Write scope**: `--scope`/`--scope-file` replace the derived scope entirely (no union: the Host passes its payload
  scope whole when it differs). Otherwise, by the unit's workflow: `sdd-proposal` the proposal directory;
  `sdd-spec-*` the unit directory, each literal `_Boundary:` path of `tasks.md` (the existing
  `devkit_spec.entrypoints.bundle` parser), the unit's materials directory
  `docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/`, each `file` of `reconcile.md` `targets` and the feedback file of
  each FB ID the spec's `Source feedback` section links. Each entry carries its source (`unit`, `boundary` with its
  task, `materials`, `reconcile`, `source-feedback` with its ID, `argument`). A `tasks.md` or `reconcile.md` that
  the parser refuses, an FB ID with no file or another workflow leaves the outside-scope check `not-run` with that
  cause (the other checks still run). The derived scope is never widened: a follow-up draft proposal a Planning
  worker adds, or a link repair outside the declared paths, is reported outside the scope for the Host to judge.
- **Base checkout**: `--base-checkout`, else the worktree's registered base checkout (the one whose Git directory is
  the common one, as `devkit worktree` locates it); absent when the command runs in the base checkout itself. Its
  HEAD and dirty paths are information, not a check: comparing them with what the Host recorded before spawning
  stays the Host's step.
- A could-not-run code's action is to pass the named flag. Each input in the result names its value and its source
  (`argument` or the derivation used).
- Each check reports `pass`, `fail` or `not-run` (with its cause), so a check that could not run is distinct from a
  negative result. The checks: ancestry of base to returned head; worktree HEAD equals the returned head; changed paths of
  `git diff --name-only <base> <head>` with those outside the scope (`not-run` when no scope could be derived and
  none was given, leaving the judgment to the Host); worktree status; `devkit workflow envelope check`
  results (malformed files, `blocked`, `pending_questions`); the cumulative rules check over the range (the
  `devkit rules check --ci --base <base>` evaluation, run only when the worktree HEAD equals the returned head,
  otherwise `not-run`); and the stage `devkit workflow next` names.
- Exit codes follow the convention: `0` every check passed, `1` at least one check failed (a negative result, not a
  refusal), `2` the command could not run (bad arguments, not a Git worktree, unknown refs, or an input neither
  given nor derivable: `WORKER_UNIT_UNRESOLVED`, `WORKER_HEAD_UNRESOLVED`, `WORKER_BASE_UNRESOLVED`). A `not-run` check alone
  does not make the exit `1`; it is reported as a notice.
- Structured output (`--format json`) is one object with the `inputs` (`unit`, `base`, `head`, `base_checkout`,
  each with its value and source), `scope` (its entries with their sources), the compared `base` and `head`,
  `changed_paths`, `outside_scope` (absent when the scope check is `not-run`), `base_checkout` (its `head` and
  `dirty_paths`, absent without one) and the per-check results; this object, or its `base`, `head` and `changed_paths`, is what the Host
  passes a read-only reviewer.
- The command modifies no file, writes no record, runs no `devkit sync`, merges nothing, retries nothing and enlarges
  no scope. Whether a finding blocks the worker's result stays the Host's decision under the existing
  `spec-delegate` procedure.

## 5. Consequences

- The Host's per-range validation becomes one call, usually without arguments; its decision and recording (accept, or block with a `worker`
  envelope) are unchanged.
- Reviewer payloads can carry a generated changed-path list instead of the caller's selection.
- A derived scope can differ from the payload scope the Host wrote (a payload that adds paths the documents do not
  declare); the Host then passes its scope with `--scope`, and the result names the scope's source either way.
- Deriving the base reads the unit's records at an earlier commit, so the envelope check must run on a committed
  tree, not only on the working directory.
- The rules check over the range is as costly as `devkit rules check --ci`; the command runs it once per call.
