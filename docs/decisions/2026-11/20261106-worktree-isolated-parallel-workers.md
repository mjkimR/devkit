---
id: ADR-worktree-isolated-parallel-workers
title: Separate worktrees for concurrent adaptive writers
summary: "For concurrent adaptive writers, we propose one worktree per writer with bounded ownership and combined-result checks, to avoid same-checkout interference, accepting setup cost and remaining merge conflicts."
proposal: SPEC-adaptive-swarm-development
status: accepted
created_at: 2026-11-06
---

# [ADR-worktree-isolated-parallel-workers] Separate worktrees for concurrent adaptive writers

## 1. Context & Problem Statement

Concurrent writers in one checkout share files, index and HEAD even when their nominal file sets are disjoint.
Separate worktrees avoid same-checkout interference but share repository metadata and may still produce conflicting
changes. Nested delegation adds a parent writer that must not race its children.

The catalog bundle installs independently of the harness, so availability of `devkit worktree` cannot be assumed.

## 2. Decision Drivers

- Give each concurrent writer an identifiable source and exclusive working checkout.
- Keep child ownership within the parent assignment.
- Preserve independent installation and existing Git authority.
- Verify combined and landed results rather than infer success from worker checks.
- Preserve incomplete results through interruption and cleanup.

## 3. Considered Options

- Shared checkout with disjoint file instructions: low setup cost, but shared index/HEAD and accidental cross-writes remain.
- Serialized writers in one checkout: simple ownership and no concurrent writes, with no writing parallelism.
- Separate worktree per concurrent writer: independent checkout state and local checks, with setup cost and merge conflicts.
- Patch-only return: serial application is possible, but executable verification needs a materialized working tree.

## 4. Decision Outcome

The proposed choice is separate worktrees for concurrent writers, with serialized execution as the fallback.

- Each concurrent writing agent, including a second-level child, owns a separate worktree and an explicit write boundary.
- A parent performs no concurrent writes in a child's worktree; it integrates shared glue after children finish.
- Use the existing harness lifecycle when available, otherwise the consuming project's documented Git procedure.
  Missing permission or tooling causes serialized work rather than automatic installation or host-setting changes.
- A worker receives explicit permitted Git operations and reports base/final identity, changed paths and actual checks.
- The Host integrates accepted results serially and verifies the combined source and applicable final target SHA.
- Cleanup waits for active writers and preserves dirty worktrees and unmerged results until retained or separately
  authorized for removal.

`PROP-adaptive-swarm-development-target` describes the prospective capability clauses. Separate worktrees reduce
same-checkout interference; they do not guarantee native path confinement, a compilable checkout, conflict-free merges
or isolation of databases, ports, caches and other external test resources.

## 5. Consequences

- Workers can run local checks against their own materialized changes.
- Boundary checks and interface coordination remain necessary after worktree isolation.
- Worktree setup and dependency initialization add cost; small tasks can remain direct or sequential.
- Shared external test resources need project-specific isolation when the selected checks use them.
- An interrupted run may intentionally retain worktrees for recovery.

## 6. Confirmation

Planned representative exercises cover two writing workers, parent/child ownership, a semantic integration conflict,
a failed combined check and interrupted cleanup. Tests identify the source SHA and retained worktree state.
Review only for assignment compliance where the host provides emulated boundaries; no zero-conflict claim is made.
