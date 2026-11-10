---
id: MS-adaptive-development-runtime
title: Adaptive development distribution and deterministic delegation support
summary: "Gives adaptive development its own distribution that can carry code, and commands that record delegated assignments and verify returned results, so large parallel builds resume and complete on recorded state instead of conversation memory."
status: planned
created_at: 2026-11-10
depends_on: []
---

# [MS-adaptive-development-runtime] Adaptive development distribution and deterministic delegation support

## Goal

Advances `ARCH-01-introduction-and-goals` §1.1 (Asset Distribution & Guidance Delivery), §1.3 (Delivery Workflow
Orchestration) and §1.8 (Task Worktrees) for adaptive development used in large initial builds with parallel writers.

Adaptive development (`CAP-DLV-adaptive-development`) is guidance only. The Host keeps the assignment board in its
context and checks returned work by hand, so an interruption or context compaction loses outstanding assignments and
a completion claim rests on the Host's reading of a diff. `MAT-adaptive-runtime-references` shows that comparable
harnesses write this state in code at the moment of each event and gate completion on it.

The milestone moves adaptive development out of the content-only catalog into a distribution that can carry code,
then adds deterministic support for delegation: recorded assignments and a verification of each returned result
against its assignment.

## Exit condition

- Adaptive development assets ship from their own distribution, install without `devkit-spec`, and existing
  selections of the bundle keep working or have a documented migration.
- A Host can record each delegated assignment with its owner, source identity, write scope and checks, and can list
  outstanding assignments after an interruption without relying on conversation history.
- A returned result can be verified against its assignment by a command: changed paths against the write scope,
  source identity against the assigned base and declared checks against recorded outcomes.
- The guidance uses these commands where they apply and keeps its existing fallback where they are unavailable.
- Host lifecycle gates for adaptive delegation (`Stop`, `SubagentStop`, `SessionStart`) have a recorded decision
  based on a measured effect and a sized host adapter change (`CAP-HOST-lifecycle-observation`), and are delivered
  only if that decision accepts them.

## Non-goals

- **Scope Excluded**: Delivering host lifecycle gates before their investigation supports them.
- **Scope Excluded**: A process runner or scheduler, model or keyword routing and compaction handling.
- **Scope Excluded**: Per-change SDD records, approvals or envelopes in adaptive development.

## Completion review

Decomposition: pending
Direct proposal work: pending
