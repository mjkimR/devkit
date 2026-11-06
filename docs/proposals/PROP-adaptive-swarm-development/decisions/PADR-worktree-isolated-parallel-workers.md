---
id: PADR-worktree-isolated-parallel-workers
title: Worktree-isolated parallel workers
summary: For parallel swarm code authoring, we isolate workers using explicit file boundary contracts and devkit worktrees, to eliminate concurrent write collisions and merge conflicts, accepting the local git worktree creation overhead.
proposal: PROP-adaptive-swarm-development
status: draft
created_at: 2026-11-06
---

# [PADR-worktree-isolated-parallel-workers] Worktree-isolated parallel workers

- **Status**: Draft
- **Date**: 2026-11-06

---

## 1. Context & Problem Statement

When multiple AI coding agents execute simultaneously in a shared workspace, they frequently attempt to modify the same
files or shared module indices concurrently. This causes race conditions, corrupted file syntax, lost edits, and git merge
conflicts. Pure prompt-based multi-agent frameworks (such as default MetaGPT or chat-based swarms) suffer repeatedly from
this failure mode because they lack filesystem-level isolation primitives.

## 2. Decision Drivers

- **Concurrency Without File Collisions**: Multiple builders must be able to generate code and tests in parallel without overwriting each other's changes.
- **Deterministic Merge and Integration**: Each worker's contributions must be verifiable and cleanly integrated into the target branch.
- **Fail-Fast Defect Isolation**: A regression caused by one builder must not block or pollute another builder's working state.
- **Reuse of devkit Harness**: Leverage existing `devkit worktree` and git operator primitives without inventing external daemons.

## 3. Considered Options

- **Option 1: Shared Directory with Prompt Constraints**: All agents operate in the single working tree, relying strictly on prompt admonitions not to edit overlapping files. Rejected because LLM agents frequently drift outside instructed boundaries, leading to corrupted states.
- **Option 2: Patch/Diff Hand-off via In-Memory Strings**: Workers return patch strings or text diffs to the coordinator, which applies them sequentially. Rejected because workers cannot run compilers, linters, or local unit tests against an unapplied patch.
- **Option 3: Worktree-Isolated Execution**: Each builder receives an isolated git worktree via `devkit worktree create` and an explicit file touch boundary (`_Boundary`). Workers commit their bounded changes locally, and the coordinator integrates them sequentially.

## 4. Decision Outcome

We choose **Option 3: Worktree-Isolated Execution**.

- The architect partitions work into disjoint file boundary contracts (`_Boundary`) prior to implementation. → `CAP-DLV-adaptive-development` rule 13 (MUST).
- Parallel builders run in independent git worktrees created via devkit's worktree lifecycle management.
- Each builder verifies its local changes with package unit tests before signaling completion.
- The coordinator merges worker branches sequentially, resolving any residual interface glue before triggering the QA tester.

## 5. Consequences

- **Positive**: Zero concurrent file overwrite collisions. Each builder has a clean, compilable environment.
- **Positive**: Builders can execute tests locally in their own worktree without interfering with peer workers.
- **Negative / Trade-off**: Worktree creation introduces slight filesystem and disk overhead (git checkout setup).
- **Follow-up**: Ensure cleanup routines remove temporary worktrees when the swarm session completes or is cancelled.

## 6. Confirmation

Integration tests verify that parallel workers operating in isolated worktrees commit distinct changes without index locks or file collision errors. Review verifies that worktree cleanup runs on session completion.
