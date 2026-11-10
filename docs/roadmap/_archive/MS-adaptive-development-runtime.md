---
id: MS-adaptive-development-runtime
title: Adaptive development distribution and deterministic delegation support
summary: "Gives adaptive development its own distribution that can carry code, and commands that record delegated assignments and verify returned results, so large parallel builds resume and complete on recorded state instead of conversation memory."
status: done
created_at: 2026-11-10
depends_on: []
---

# [MS-adaptive-development-runtime] Adaptive development distribution and deterministic delegation support

## Goal

Advances `ARCH-01-introduction-and-goals` §1.1 (Asset Distribution & Guidance Delivery), §1.3 (Delivery Workflow
Orchestration) and §1.8 (Task Worktrees) for adaptive development used in large initial builds with parallel writers.

The milestone delivers a distribution that carries adaptive development assets and commands, plus deterministic
support for recording delegated assignments and verifying each returned result against its assignment.
`CAP-DLV-adaptive-assignments` defines that command boundary. Lifecycle hook gates are excluded by
`ADR-reject-adaptive-lifecycle-hooks`; no live hook effect measurement is claimed.

## Exit condition

- Adaptive development assets ship from their own distribution, install without `devkit-spec`, and existing
  selections of the bundle keep working or have a documented migration.
- A Host can record each delegated assignment with its owner, source identity, write scope and checks, and can list
  outstanding assignments after an interruption without relying on conversation history.
- A returned result can be verified against its assignment by a command: changed paths against the write scope,
  source identity against the assigned base and declared checks against recorded outcomes.
- The guidance uses these commands where they apply and keeps its existing fallback where they are unavailable.
- Lifecycle hook scope has an explicit disposition: `ADR-reject-adaptive-lifecycle-hooks` rejects delivery,
  and `MAT-adaptive-lifecycle-hooks` retains the host capability analysis and sized adapter options. Measurement
  and hook delivery are outside the completed scope.

## Non-goals

- **Scope Excluded**: Lifecycle hook gates and a live effect measurement program, as decided in
  `ADR-reject-adaptive-lifecycle-hooks`. Recurring F1 or F2 observations require a new proposal.
- **Scope Excluded**: A process runner or scheduler, model or keyword routing and compaction handling.
- **Scope Excluded**: Per-change SDD records, approvals or envelopes in adaptive development.

## Completion review

Decomposition: confirmed
Direct proposal work: confirmed

- `SPEC-adaptive-package-extraction` is completed and integrated; adaptive assets ship in `devkit-adaptive`.
- `SPEC-adaptive-assignment-cli` is completed and integrated; its commands record, resume and verify delegated
  assignments, and the delivered guidance uses them with its documented fallback.
- The lifecycle hook proposal was rejected and retired through `ADR-reject-adaptive-lifecycle-hooks`; no delivery
  or measurement remains in this milestone's agreed scope.
- The three original direct proposals account for the retained scope. No unsettled direct member remains.
