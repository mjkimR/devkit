---
id: SPEC-delegation-sandbox-guidance
title: Delegation scope and sandbox guidance fixes
summary: Resolves five open feedback items on delegated write scope, worker-producible baselines, reviewer probe tests and sandbox-safe worktree and Git metadata access in the spec bundle's guidance and role contracts.
status: in-progress
created: 2026-10-26
related_capabilities: [CAP-DLV-delivery-workflows]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-delegation-sandbox-guidance] Delegation scope and sandbox guidance fixes

## 1. Problem Statement & Motivation

Five delegated runs hit the same kind of gap: the role contract or the payload guidance did not cover an operation
the agreed work needed, so the agent worked around it and left the cost to the Host.

- A `development-worker` that changed a selected bundle could not run the `devkit sync` the change implies, because
  the write scope did not name the tracked files sync writes.
- A before/after acceptance outcome measured "on the integration base" needs a second checkout, which a worker's
  commit-only Git rights forbid.
- The `code-reviewer` contract forbids every write, so a reviewer that suspects an ordering or reactivity defect can
  only reason about it instead of running a probe test.
- A task worktree is created beside the base checkout, which can lie outside the session's writable roots, and a
  linked worktree's commits update Git metadata in the shared Git directory, which can also lie outside them. The
  `spec` skill's worktree procedure says neither.

## 2. User Stories

- **US-1**: As a Host delegating a bundle change, I want the payload guidance to put the tracked sync outputs in the
  write scope, so that the worker leaves a synchronized repository.
- **US-2**: As a development worker, I want every before/after outcome to name a baseline I can produce in my
  worktree, or to leave the base measurement to the Host, so that I never need a second checkout.
- **US-3**: As a code reviewer, I want to run throwaway probe tests in an ignored path, so that a timing or ordering
  finding arrives with a failing probe.
- **US-4**: As an agent in a sandboxed session, I want the worktree procedure to state where task worktrees and their
  Git metadata live and which route is permitted when either is outside my writable roots.

## 3. Non-Goals

1. **Scope Excluded**: No CLI, schema or code change. `devkit worktree start` keeps its fixed path rule; this unit
   adds no option to relocate a worktree.
2. **Scope Excluded**: No host setting, sandbox configuration or approval policy is added or recommended for the
   agent to change.
3. **Scope Excluded**: No change to the support-role diff check in `spec-delegate`, because an ignored probe path
   already leaves `git status --short` unchanged.
4. **Scope Excluded**: The second half of `FB-bundle-change-needs-sync-scope` (documents found for changed scripts) is
   already covered: the worker's write scope includes the Living Spec paths the reconcile record targets. This unit
   adds nothing for it.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Bundle changes carry their sync outputs into the write scope
- **Given** a delegated task whose `_Boundary:` includes a bundle source the project selects
- **When** the Host builds the `development-worker` payload per `spec-delegate`'s `references/payload.md`
- **Then** the guidance tells it to add the tracked files `devkit sync --check` lists for that change (for example
  `.devkit/installation.json` and the managed `AGENTS.md` block) to the write scope, and the `development-worker`
  contract tells the worker to run `devkit sync` after the bundle edit and commit those files, never editing
  `.devkit/managed/` by hand.

### [AC-02] Before/after outcomes name a worker-producible baseline
- **Given** a Planning turn whose proposal states a before/after outcome measured against the base
- **When** the runner follows the `spec` skill's `references/planning.md`
- **Then** the step tells it to name a baseline a development worker can produce in its worktree (the head with the
  change disabled, or a Planning measurement on the same machine recorded in `materials/`) or to state that the Host
  takes the base measurement, and the `development-worker` contract tells the worker to use that baseline, never to
  check out the base, and to report a base measurement it cannot produce in its `worker` envelope.

### [AC-03] The code reviewer may run probe tests in an ignored path
- **Given** a `code-reviewer` run with an ignored probe path inside the worktree
- **When** the reviewer wants executable evidence for a finding
- **Then** its contract allows throwaway probe tests only under that ignored path, run with the package's test
  command and deleted before it returns, keeps "modify, stage and commit nothing" for every other path, keeps
  `git status --short` unchanged, and states that probes never count as the unit's tests; the `code-reviewer`
  payload row names the probe path.

### [AC-04] The worktree procedure states the sandbox-safe route
- **Given** a session whose writable roots exclude the default sibling worktree path or the shared Git directory
- **When** the agent follows the `spec` skill's `references/worktree.md`
- **Then** the procedure states that the task worktree is always `<parent of base>/<base name>-wt-<branch>` and
  `--workspace-root` only selects the checkout, that a linked worktree's commits write the shared Git directory of
  the base, and that the permitted route is the host's own per-operation approval or writable roots the user grants,
  never moving the worktree, re-creating it elsewhere or changing a host setting.

### [AC-05] Source feedback is resolved
- **Given** the five source feedback files
- **When** this unit's implementation is complete
- **Then** each has `status: resolved` and a `Disposition` section naming `SPEC-delegation-sandbox-guidance` and the
  changed guidance.

## 5. Assumptions

- `FB-worktree-sandbox-location` proposed `--workspace-root` as the way to place worktrees inside writable roots. The
  code (`path_for` in `devkit_agt.features.worktree.usecases.lifecycle`), its tests and `CAP-WT-task-worktrees` fix
  the path beside the base; `--workspace-root` only names a directory inside the checkout. The guidance documents the
  actual behaviour and the permitted route instead, which stays inside the agreed goal of sandbox-safe worktree
  guidance.
- The write scope names `worktree.md` and `development-worker.md`; their sources are the `.jinja` files of the same
  names, which this unit edits.

## Source feedback

- `FB-bundle-change-needs-sync-scope`
- `FB-base-measurement-outside-worker-git`
- `FB-reviewer-probe-tests`
- `FB-worktree-sandbox-location`
- `FB-git-metadata-sandbox-boundary`
