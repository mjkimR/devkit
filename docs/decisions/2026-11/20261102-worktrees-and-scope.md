---
id: ADR-worktrees-and-scope
title: Worktree levels, branch guards and host-observed work scope
summary: "For task isolation and the shared work-scope registry, we use auto/required levels, guard units to dev-<slug> in every checkout, clean up after finish, keep Git storage with side-effect-free reads and let the Host observe scope, to keep parallel work safe, accepting incomplete remote visibility."
status: accepted
created_at: 2026-11-02
aliases:
  - ADR-worktrees-branches-and-scope
  - ADR-scope-maintenance-through-skills
  - ADR-cleanup-after-worktree-finish
  - ADR-worktree-and-pull-request-levels
  - ADR-branch-guards-and-close-discard
  - ADR-keep-shared-storage-and-separate-read-access
  - ADR-host-owned-scope-observation
---

# [ADR-worktrees-and-scope] Worktree levels, branch guards and host-observed work scope

Superseded in part by `ADR-collect-only-scope-observation`: in §4 "Host-owned scope observation", the clause that `scope collect`
has `snapshot`, `refs` and default `worktrees` modes, and the clause that the maintenance `update` stays directly
callable with its existing ACK contract; in §6, the clause that the maintenance ACK tests remain regression checks.
Its other decisions, including opt-in fetch, bounded deadlines, read-only collection, the ownership tests and the
post-finish cleanup, remain in force; its wording about `query` and history reads (§4 "Registry storage and read
access", §5, §6) is reworded to the remaining read surfaces without changing those decisions.

Superseded in part by `ADR-single-local-landing-route`: the clause that `[worktree] pull_request = "required"` makes devkit refuse `devkit worktree finish --merge`. All other decisions remain in force.

- **Status**: Accepted
- **Date**: 2026-11-02
- **Deciders**: @mjkimR
- **Involved Components/Capabilities**: `CAP-DLV-project-policy`, `CAP-DLV-spec-bundles`,
  `CAP-DLV-proposal-planning`, `CAP-COLL-work-scope-registry`, `CAP-HARN-agent-guidance`, `ARCH-06-runtime-view`,
  `ARCH-08-cross-cutting`

---

## 1. Context & Problem Statement

`devkit workflow next` and `devkit worktree finish` know nothing about devkit-spec, yet the work-scope registry has to
follow each task from registration to cleanup. The two steps after a finish (`devkit spec scope sweep --apply`,
`devkit spec proposal prune <slug>`) are exactly the ones an agent forgets once the merge is done, and a forgotten
sweep leaves a stale record every other worktree sees. devkit has `devkit.post_finish` entry points, called after a
successful `devkit worktree finish`, under the rules of its `devkit.post_sync` extensions (an extension never fails
the command).

`[tool.spec] worktree` and devkit's `[worktree] pull_request` were switches that forced one behavior on every task.
Agents need to use them when a task needs them, and projects need to require them when they manage work that way. The
location of both keys is settled by `ADR-document-system`. With activity branches
(`ADR-orchestration-workers`) a `direct` task may run on `dev-<slug>` in the base checkout
(`devkit worktree start --no-worktree`). In the local flow a handoff on the base branch deleted the accepted proposal
from the base, `devkit spec new` could create a unit on any branch, a base-checkout task's scope record leaked past
its finish, and a close had no allowed way to drop an unmerged branch. The strategy layer (workbench
`docs/strategy-layer/01-master-flow.md` §4.7, §7.4, `03-policy.md` §3) settles the rules.

`CAP-COLL-work-scope-registry` shares state across linked worktrees using Git directories and provides advisory
overlap evidence. Logical reads created locks and cleaned record and token temporary files, forcing write access even
when all records are readable. Worker scope refresh calls add token, retry and ACK duties without proving freshness
when the Host schedules another task. Creation already registers initial scope, while host-visible worktrees and
branch trees contain later evidence that can be read without modifying registrations.

---

## 2. Decision Drivers

- devkit stays SDD-agnostic: no devkit-spec calls inside devkit commands; the extension point is general and the
  cleanup lives in devkit-spec. (ADR-worktrees-branches-and-scope)
- Cleanup after a finish runs without a step an agent can skip. (ADR-worktrees-branches-and-scope)
- A refused finish never leaves a live task unregistered. (ADR-worktrees-branches-and-scope)
- Every step is a deterministic command an agent can run and check. (ADR-worktrees-branches-and-scope)
- Isolation and review overhead follow the task, not a fixed switch; the worktree is chosen for isolation, not by the
  integration path. (ADR-worktrees-branches-and-scope)
- A project can still make either level a rule that no agent judgment lowers. (ADR-worktrees-branches-and-scope)
- No external consumers exist, so the format changes in place without a compatibility mapping.
  (ADR-worktrees-branches-and-scope)
- A unit lands only on its own activity branch, wherever the checkout is. (ADR-worktrees-branches-and-scope)
- No force-deletion outside a decided close. (ADR-worktrees-branches-and-scope)
- Preserve the registry's discovery, ownership, revision checks and coherent concurrent reads; minimize permission
  requirements without claiming that a location or transport bypasses host authorization.
  (ADR-worktrees-branches-and-scope)
- Remove worker publication and ACK obligations. (ADR-host-owned-scope-observation)
- Make observation an explicit Host action with bounded cost. (ADR-host-owned-scope-observation)
- Preserve source attribution and report incomplete coverage. (ADR-host-owned-scope-observation)
- Keep the generic harness independent of spec observation. (ADR-host-owned-scope-observation)
- Accept local and published remote evidence without claiming distributed monitoring.
  (ADR-host-owned-scope-observation)

---

## 3. Considered Options

### Registry maintenance after a finish

- **Skills call the scope commands; sweep after a successful finish** (selected in
  `ADR-scope-maintenance-through-skills`, replaced in `ADR-cleanup-after-worktree-finish`): no devkit change; the
  registry is only as current as the skills' compliance.
- **Skills release before finish** (rejected in `ADR-scope-maintenance-through-skills`): a refused finish
  (`WORKTREE_UNMERGED`, `WORKTREE_DIRTY`, `WORKTREE_BASE_BEHIND`, ...) leaves a still-running task invisible to the
  other worktrees.
- **Hooks in devkit for devkit-spec** (rejected in `ADR-scope-maintenance-through-skills` as an extension mechanism
  for one plugin's registry).
- **A `devkit.post_finish` extension in devkit-spec** (selected in `ADR-cleanup-after-worktree-finish`): no manual
  cleanup step; a refused finish runs no extension; an extension failure is a warning the agent has to notice.
- **A `devkit spec finish` wrapper** (rejected in `ADR-cleanup-after-worktree-finish`): two finish commands; an agent
  that runs devkit's skips the cleanup.
- **Keep the cleanup in the skills** (rejected in `ADR-cleanup-after-worktree-finish`): depends on the agent
  remembering two commands after the merge.

### Worktree and pull request policy

- **`auto` and `required` levels** (selected in `ADR-worktree-and-pull-request-levels`, retained in
  `ADR-branch-guards-and-close-discard`): no value means "never", so a needed worktree or pull request is never blocked
  by configuration; agents must judge `auto` choices.
- **Keep booleans** (rejected in `ADR-worktree-and-pull-request-levels`): `false` forbids isolation a task needs;
  `true` charges every task.
- **Three levels with `off`** (rejected in `ADR-worktree-and-pull-request-levels`): forbidding has no use case found;
  an unavailable capability (no remote) is a diagnostic, not a policy.

### Branch guards

- **Branch guards in every checkout, worktree by isolation, close through `finish --discard`** (selected in
  `ADR-branch-guards-and-close-discard`): one rule for every checkout; a project that created specs on its base branch
  must start `dev-<slug>` first.
- **Keep the guards to linked worktrees** (rejected in `ADR-branch-guards-and-close-discard`): the base checkout, now a
  normal place to work, stays unguarded.

### Registry storage and read access

- **Keep Git storage with scoped mutation approval** (selected in `ADR-keep-shared-storage-and-separate-read-access`).
- **Configure shared `.devkit/state/`** and **a service-owned MCP registry** (rejected in
  `ADR-keep-shared-storage-and-separate-read-access` for this scope, not promised later): they require additional
  lifecycle and authorization design and do not inherently solve token or cross-worktree access. See
  `docs/materials/2026-10/20261020-scope-registry-sandbox-access/access-comparison.md`.

### Scope refresh

| Option | Benefit | Cost or risk |
| --- | --- | --- |
| Keep skill updates (rejected in `ADR-host-owned-scope-observation`) | Reuses existing registry operation | Workers retain maintenance duties; records can lag silently |
| Automatic `workflow next` refresh (rejected in `ADR-host-owned-scope-observation`) | Uses existing worker boundary calls | Optional-provider hook, worker token recovery and timing gaps remain |
| Handoff snapshots only (rejected in `ADR-host-owned-scope-observation`) | Smallest implementation | Cannot inspect later local declarations, dirty paths or published branch changes |
| Creation snapshots plus explicit Host observation (selected in `ADR-host-owned-scope-observation`) | Host chooses when and how much evidence to collect; no worker publication | Partial visibility and bounded scanning cost must remain explicit |
| Distributed registry/watchers now (rejected in `ADR-host-owned-scope-observation`) | Could share snapshots between machines | Requires backend, credentials, shared identity and publication contracts outside this scope |

---

## 4. Decision Outcome

### Cleanup after finish

- After a successful `devkit worktree finish`, the `devkit.post_finish` extension `devkit_spec.cleanup.after_finish`
  runs in the base checkout of a project that deploys the `spec` bundle: it prunes `docs/proposals/PROP-<slug>/` when
  empty and removes the scope records of the finished worktree, at the revision it read; other stale records wait for
  `devkit spec scope sweep --apply`. Nothing is removed unless the finish succeeded. (ADR-cleanup-after-worktree-finish)

### Worktree and pull request levels

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

### Branch guards and close

- In a Git checkout, linked or base, `devkit spec proposal handoff` (`SPEC_PROPOSAL_WRONG_WORKTREE`) and
  `devkit spec new` (`SPEC_WRONG_BRANCH`) refuse any branch but `dev-<slug>`. Outside Git nothing is checked. A slug is
  at most 59 characters so its activity branches fit devkit's 64. (ADR-branch-guards-and-close-discard)
- The work-scope registry tracks linked worktrees: a handoff or task in the base checkout registers nothing, and a
  record the base checkout holds anyway is released when its `--no-worktree` branch is finished or discarded.
  (ADR-branch-guards-and-close-discard)
- A close (depth escalation, supersede, abandon) drops the task's unmerged branch with
  `devkit worktree finish dev-<slug> --discard`, on the authority of the close's decider; no other path force-deletes a
  branch. (ADR-branch-guards-and-close-discard)

### Registry storage and read access

- The registry keeps its Git common-directory storage and per-worktree ownership tokens, with read-only access for `scope collect`.
  Shared locks on an existing read-opened safe lock file serialize record reads against exclusive writers.
  Read-only token lookup does no cleanup. Absent namespaces return empty without creation; existing namespaces missing a
  lock fail visibly. Mutations retain their present storage, ownership, cleanup and explicit permission requirements.
  No automatic fallback performs writes. (ADR-keep-shared-storage-and-separate-read-access)

### Host-owned scope observation

Creation snapshots plus explicit Host collection, as specified in `SPEC-automatic-scope-collection`.
(ADR-host-owned-scope-observation)

- Automatic creation registration stays best effort with verbose-only failure diagnostics and unchanged primary
  results, including `--strict`. No replacement worker recovery action is required. (ADR-host-owned-scope-observation)
- Worker scope registration/update/ACK duties are removed and all workflow evaluation triggers are excluded.
  (ADR-host-owned-scope-observation)
- `scope collect` has `snapshot`, `refs` and default `worktrees` modes, opt-in fetch and bounded deadlines.
  (ADR-host-owned-scope-observation)
- Collection reads consistently through filesystem or pinned-tree source adapters and leaves registry records, owner
  tokens, revisions and journal unchanged. Fetch affects only the requested remote-tracking branch namespace.
  (ADR-host-owned-scope-observation)
- Collection preserves per-source observations, deduplicates only confirmed identities with identical effective
  range/declaration inputs and exposes unknown attribution, branch-relative committed ranges, missing layers and
  comparison coverage. Explicit collection failures and partial results retain the Agent Advisory Protocol; only
  automatic creation failure handling is silent. (ADR-host-owned-scope-observation)
- Maintenance `update` is hidden in ordinary discovery while direct invocation and its existing ACK contract are
  retained. (ADR-host-owned-scope-observation)
- A cloud-backed registry repository, such as Firestore, is recorded as a future direction for cross-PC initial
  snapshot sharing. Backend implementation and cross-machine registration are excluded. PRs provide published-change
  visibility in the meantime; neither PRs nor future creation snapshots reveal later private worktree edits.
  (ADR-host-owned-scope-observation)

---

## 5. Consequences

- **Positive**:
  - The `spec` skills drop the post-finish cleanup steps; `[NOTICE]` lines (`POST_FINISH_NOTICE`) report what the
    extension removed. (ADR-cleanup-after-worktree-finish)
  - Small tasks stay in the current checkout by default; one branch rule covers every checkout; closes leave no records
    behind. (ADR-branch-guards-and-close-discard)
  - An initialized readable registry can be queried without write access.
    (ADR-keep-shared-storage-and-separate-read-access)
  - The Host can inspect an unregistered branch or accessible worktree without acquiring its token.
    (ADR-host-owned-scope-observation)
  - Worker omissions no longer control whether live host-visible evidence can be collected.
    (ADR-host-owned-scope-observation)
- **Negative / Risks**:
  - A stale record of an abandoned worktree (one never finished) still needs `devkit spec scope sweep --apply` or
    `devkit spec scope release -w <worktree>`. An extension failure is a `POST_FINISH_EXTENSION_FAILED` warning the
    agent has to notice. (ADR-cleanup-after-worktree-finish)
  - Hosts that deny read-open flock still return an error; this is not a guarantee that all sandboxed hosts permit
    queries. A newly initializing namespace may yield a retryable error until an authorized writer creates the lock.
    (ADR-keep-shared-storage-and-separate-read-access)
  - Parsing must be extracted below use cases so target documents and entrypoints use the same source as declarations.
    (ADR-host-owned-scope-observation)
  - Snapshots can be stale, remote refs can lag and another PC's dirty/unpushed work is invisible. A complete report
    means requested observable coverage, not global independence or a single atomic repository snapshot.
    (ADR-host-owned-scope-observation)
- **Follow-ups**:
  - Inline Planning for `spec` depth starts `dev-<slug>` before `devkit spec new`. (ADR-branch-guards-and-close-discard)
  - The post-finish extension releases a base-checkout record when the finish result's path is the base checkout.
    (ADR-branch-guards-and-close-discard)
  - The rejection, decomposition and close procedures name `finish --discard` and the closing answers of open questions
    (01 §5.2, §6.2, §7.4). (ADR-branch-guards-and-close-discard)
  - Development verifies lock compatibility on Linux and macOS and the absence of write calls on the read-only paths.
    (ADR-keep-shared-storage-and-separate-read-access)
  - Cross-PC snapshot sharing is reconsidered when it becomes an implementation requirement; this decision chooses no
    backend and promises no cloud adapter in this delivery. (ADR-host-owned-scope-observation)

---

## 6. Confirmation

- `packages/devkit/tests/integration/features/worktree/` (`test_branches.py`, `test_merging.py`,
  `test_pull_request.py`, `test_cli.py`): activity branches, finish and discard, and the `pull_request` levels.
  (ADR-worktrees-branches-and-scope)
- `packages/devkit-spec/tests/integration/features/delivery/test_cleanup.py`: the post-finish cleanup of the proposal
  directory and the scope record. (ADR-worktrees-branches-and-scope)
- `packages/devkit-spec/tests/integration/features/scope/`: scope registration, sweep and the read-only access
  of collection. (ADR-worktrees-branches-and-scope)
- Development verifies AC-01–AC-08 in `SPEC-automatic-scope-collection` with scope/delivery integration tests and
  source bundle guidance checks. Tests cover no token/registry writes, pinned-ref inputs, divergent refs, malformed or
  absent inputs, source/total deadlines, comparison truncation, dense-output/input size limits, fetch outcomes and
  strict/non-strict output. Existing ownership, maintenance ACK and post-finish cleanup tests remain regression
  checks. Planning evidence does not substitute for these runtime checks. Guidance about PRs and future cloud storage
  is Review only. (ADR-host-owned-scope-observation)
