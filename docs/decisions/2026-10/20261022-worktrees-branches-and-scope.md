---
id: ADR-worktrees-branches-and-scope
title: Worktree Levels, Branch Guards and Work-Scope Registry Maintenance
summary: "For task isolation and the shared work-scope registry, we use auto/required levels, guard units to dev-<slug> in every checkout, clean up through a post-finish extension and keep Git storage with side-effect-free reads, to keep parallel work safe, accepting skill-maintained records."
status: accepted
superseded_by: ADR-host-owned-scope-observation
created_at: 2026-10-22
aliases:
  - ADR-scope-maintenance-through-skills
  - ADR-cleanup-after-worktree-finish
  - ADR-worktree-and-pull-request-levels
  - ADR-branch-guards-and-close-discard
  - ADR-keep-shared-storage-and-separate-read-access
---

# [ADR-worktrees-branches-and-scope] Worktree Levels, Branch Guards and Work-Scope Registry Maintenance

- **Status**: Accepted
- **Date**: 2026-10-22
- **Deciders**: @mjkimR
- **Involved Components/Capabilities**: `CAP-DLV-project-policy`, `CAP-DLV-spec-bundles`,
  `CAP-DLV-proposal-planning`, `CAP-COLL-work-scope-registry`, `CAP-HARN-agent-guidance`, `ARCH-06-runtime-view`,
  `ARCH-08-cross-cutting`

---

## 1. Context & Problem Statement

In a monolithic architecture the work-scope registry was kept current by tightly coupled commands. In devkit,
`devkit workflow next` and `devkit worktree finish` know nothing about devkit-spec, yet the registry still has to
follow each task from registration to cleanup. Leaving every cleanup step to the skills meant the two steps after a
finish (`devkit spec scope sweep --apply`, `devkit spec proposal prune <slug>`) were exactly the ones an agent forgets
once the merge is done, and a forgotten sweep leaves a stale record every other worktree sees. devkit has since gained
`devkit.post_finish` entry points, called after a successful `devkit worktree finish`, under the rules of its
`devkit.post_sync` extensions (an extension never fails the command).

`[tool.spec] worktree` and devkit's `[worktree] pull_request` were switches that forced one behavior on every task.
Agents need to use them when a task needs them, and projects need to require them when they manage work that way. The
location of both keys is settled by `ADR-spec-package-on-devkit`. With activity branches
(`ADR-orchestration-workers`) a `direct` task may run on `dev-<slug>` in the base checkout
(`devkit worktree start --no-worktree`). A review of the local flow found that a handoff on the base branch deleted the
accepted proposal from the base, that `devkit spec new` could create a unit on any branch, that a base-checkout task's
scope record leaked past its finish, and that a close had no allowed way to drop an unmerged branch. The strategy layer
(workbench `docs/strategy-layer/01-master-flow.md` §4.7, §7.4, `03-policy.md` §3) settles the rules.

`CAP-COLL-work-scope-registry` shares state across linked worktrees using Git directories. Logical reads created
locks and cleaned record and token temporary files, forcing write access even when all records are readable.

---

## 2. Decision Drivers

- devkit stays SDD-agnostic: no devkit-spec calls inside devkit commands; the extension point is general and the
  cleanup lives in devkit-spec.
- Cleanup after a finish runs without a step an agent can skip.
- A refused finish never leaves a live task unregistered.
- Every step is a deterministic command an agent can run and check.
- Isolation and review overhead follow the task, not a fixed switch; the worktree is chosen for isolation, not by the
  integration path.
- A project can still make either level a rule that no agent judgment lowers.
- No external consumers exist, so the format changes in place without a compatibility mapping.
- A unit lands only on its own activity branch, wherever the checkout is.
- No force-deletion outside a decided close.
- Preserve the registry's discovery, ownership, revision checks and coherent concurrent reads; minimize permission
  requirements without claiming that a location or transport bypasses host authorization.

---

## 3. Considered Options

### Registry maintenance after a finish
- **Skills call the scope commands; sweep after a successful finish** (selected by
  `ADR-scope-maintenance-through-skills`, superseded by `ADR-cleanup-after-worktree-finish`): no devkit change; the
  registry is only as current as the skills' compliance.
- **Skills release before finish** (rejected by `ADR-scope-maintenance-through-skills`): a refused finish
  (`WORKTREE_UNMERGED`, `WORKTREE_DIRTY`, `WORKTREE_BASE_BEHIND`, ...) leaves a still-running task invisible to the other
  worktrees.
- **Hooks in devkit for devkit-spec** (rejected by `ADR-scope-maintenance-through-skills` as an extension mechanism for
  one plugin's registry).
- **A `devkit.post_finish` extension in devkit-spec** (selected by `ADR-cleanup-after-worktree-finish`): no manual
  cleanup step; a refused finish runs no extension; an extension failure is a warning the agent has to notice.
- **A `devkit spec finish` wrapper** (rejected by `ADR-cleanup-after-worktree-finish`): two finish commands; an agent
  that runs devkit's skips the cleanup.
- **Keep the cleanup in the skills** (rejected by `ADR-cleanup-after-worktree-finish`): depends on the agent
  remembering two commands after the merge.

### Worktree and pull request policy
- **`auto` and `required` levels** (selected by `ADR-worktree-and-pull-request-levels`, retained by
  `ADR-branch-guards-and-close-discard`): no value means "never", so a needed worktree or pull request is never blocked
  by configuration; agents must judge `auto` choices.
- **Keep booleans** (rejected by `ADR-worktree-and-pull-request-levels`): `false` forbids isolation a task needs;
  `true` charges every task.
- **Three levels with `off`** (rejected by `ADR-worktree-and-pull-request-levels`): forbidding has no use case found;
  an unavailable capability (no remote) is a diagnostic, not a policy.

### Branch guards
- **Branch guards in every checkout, worktree by isolation, close through `finish --discard`** (selected by
  `ADR-branch-guards-and-close-discard`): one rule for every checkout; a project that created specs on its base branch
  must start `dev-<slug>` first.
- **Keep the guards to linked worktrees** (rejected by `ADR-branch-guards-and-close-discard`): the base checkout, now a
  normal place to work, stays unguarded.

### Registry storage and read access
- **Keep Git storage with scoped mutation approval** (selected by `ADR-keep-shared-storage-and-separate-read-access`).
- **Configure shared `.devkit/state/`** and **a service-owned MCP registry** (rejected by
  `ADR-keep-shared-storage-and-separate-read-access` for this scope, not promised later): they require additional
  lifecycle and authorization design and do not inherently solve token or cross-worktree access. See
  `docs/materials/2026-10/20261020-scope-registry-sandbox-access/access-comparison.md`.

---

## 4. Decision Outcome

- After a successful `devkit worktree finish`, the `devkit.post_finish` extension `devkit_spec.cleanup.after_finish`
  runs in the base checkout of a project that deploys the `spec` bundle: it prunes `docs/proposals/PROP-<slug>/` when
  empty and removes the scope records of the finished worktree, at the revision it read; other stale records wait for
  `devkit spec scope sweep --apply`. Nothing is removed unless the finish succeeded. (ADR-cleanup-after-worktree-finish)
- Registration (`devkit spec new`, handoff) and updates (`spec-tasks`, `spec-sync`) stay with the skills.
  (ADR-cleanup-after-worktree-finish)
- `[tool.spec] worktree` and devkit's `[worktree] pull_request` are `"auto"` (default) or `"required"`; a boolean is
  rejected (`SPEC_CONFIG_INVALID` for `[tool.spec] worktree`, `WORKTREE_CONFIG_INVALID` for `pull_request`).
  (ADR-branch-guards-and-close-discard)
- `[tool.spec] worktree` applies to `direct` mode: `required` runs every `spec` and `proposal` activity in a worktree;
  under `auto` a worktree is used when the checkout holds unrelated changes, another task is in flight there or the
  user asks. The integration path does not choose it: a pull-request-bound task may run on its branch in the current
  checkout. (ADR-branch-guards-and-close-discard)
- `[worktree] pull_request = "required"` integrates every task through a pull request and makes devkit refuse
  `devkit worktree finish --merge`. (ADR-worktree-and-pull-request-levels, levels retained by
  ADR-branch-guards-and-close-discard)
- In a Git checkout, linked or base, `devkit spec proposal handoff` (`SPEC_PROPOSAL_WRONG_WORKTREE`) and
  `devkit spec new` (`SPEC_WRONG_BRANCH`) refuse any branch but `dev-<slug>`. Outside Git nothing is checked. A slug is
  at most 59 characters so its activity branches fit devkit's 64. (ADR-branch-guards-and-close-discard)
- The work-scope registry tracks linked worktrees: a handoff or task in the base checkout registers nothing, and a
  record the base checkout holds anyway is released when its `--no-worktree` branch is finished or discarded.
  (ADR-branch-guards-and-close-discard)
- A close (depth escalation, supersede, abandon) drops the task's unmerged branch with
  `devkit worktree finish dev-<slug> --discard`, on the authority of the close's decider; no other path force-deletes a
  branch. (ADR-branch-guards-and-close-discard)
- The registry keeps its Git common-directory storage and per-worktree ownership tokens, with a read-only query path.
  Shared locks on an existing read-opened safe lock file serialize record and history reads against exclusive writers.
  Query token lookup does no cleanup. Absent namespaces return empty without creation; existing namespaces missing a
  lock fail visibly. Mutations retain their present storage, ownership, cleanup and explicit permission requirements.
  No automatic fallback performs writes. (ADR-keep-shared-storage-and-separate-read-access)

---

## 5. Consequences

- **Positive**:
  - The `spec` skills drop the post-finish cleanup steps; `[NOTICE]` lines (`POST_FINISH_NOTICE`) report what the
    extension removed. (ADR-cleanup-after-worktree-finish)
  - Small tasks stay in the current checkout by default; one branch rule covers every checkout; closes leave no records
    behind. (ADR-branch-guards-and-close-discard)
  - An initialized readable registry can be queried without write access.
    (ADR-keep-shared-storage-and-separate-read-access)
- **Negative / Risks**:
  - The registry is still only as current as the skills' register and update steps; a stale record of an abandoned
    worktree (one never finished) still needs `devkit spec scope sweep --apply` or
    `devkit spec scope release -w <worktree>`. An extension failure is a `POST_FINISH_EXTENSION_FAILED` warning the
    agent has to notice. (ADR-cleanup-after-worktree-finish)
  - Hosts that deny read-open flock still return an error; this is not a guarantee that all sandboxed hosts permit
    queries. A newly initializing namespace may yield a retryable error until an authorized writer creates the lock.
    (ADR-keep-shared-storage-and-separate-read-access)
- **Follow-ups**:
  - Inline Planning for `spec` depth starts `dev-<slug>` before `devkit spec new`. (ADR-branch-guards-and-close-discard)
  - The post-finish extension releases a base-checkout record when the finish result's path is the base checkout.
    (ADR-branch-guards-and-close-discard)
  - The rejection, decomposition and close procedures name `finish --discard` and the closing answers of open questions
    (01 §5.2, §6.2, §7.4). (ADR-branch-guards-and-close-discard)
  - Development verifies lock compatibility on Linux and macOS and query-wide absence of write calls.
    (ADR-keep-shared-storage-and-separate-read-access)

---

## 6. Confirmation

- `packages/devkit/tests/integration/features/worktree/` (`test_branches.py`, `test_merging.py`,
  `test_pull_request.py`, `test_cli.py`): activity branches, finish and discard, and the `pull_request` levels.
- `packages/devkit-spec/tests/integration/features/delivery/test_cleanup.py`: the post-finish cleanup of the proposal
  directory and the scope record.
- `packages/devkit-spec/tests/integration/features/scope/`: scope registration, query, sweep and the read-only access
  of queries.
