---
id: SPEC-handoff-fixture-initialization
title: Reuse isolated handoff test initialization
summary: "Reuse synchronized standalone repository templates in handoff tests while preserving independent Git state and real Planning worktree creation."
status: in-progress
created: 2026-10-20
related_capabilities: []
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-handoff-fixture-initialization] Reuse isolated handoff test initialization

## 1. Problem Statement & Motivation

The handoff integration fixture repeats asset synchronization and preparation commits for every case. Diagnostic
runs attributed 39.94 serial seconds to twelve fixture setups, including 22.02 seconds in repeated synchronization.
Reusing a prepared repository reduced diagnostic elapsed time, but copying completed linked-worktree state changed
the initial topology. The implementation reuses only the standalone initialization before Planning worktree creation.

## 2. User Stories

- As a developer or coding agent, I want repeated handoff tests to reuse initialization so that verification spends
  less time preparing identical repositories while continuing to test real approvals, Git and registration behavior.

## 3. Non-Goals

- Changing production code, the affected-test selector, test selection or subprocess behavior under test.
- Caching repositories across pytest executions or sharing mutable repositories between workers or tests.
- Optimizing unrelated integration fixtures or changing workflow and handoff contracts.

## 4. Acceptance Criteria

### [AC-01] Reuse standalone initialization
- **Given** multiple handoff cases in one pytest worker,
- **When** their fixtures run,
- **Then** synchronization and its preparation commit execute once per template fixture lifetime, and each case
  receives a copy before creating its own real Planning worktree and accepted proposal.

### [AC-02] Isolate mutable Git and ignored assets
- **Given** an initialized template and a case repository,
- **When** the case changes Git refs, local configuration, tracked files or ignored managed assets,
- **Then** the template remains unchanged, Git directories resolve inside their respective repositories, and the
  case's registered worktrees reference only that case's repository and Planning checkout.

### [AC-03] Preserve handoff verification
- **Given** the existing integration test cases,
- **When** the integration file and affected tests execute,
- **Then** existing assertions pass without new skips, and approval, stale-base, language, cancellation and native
  registration operations retain their real implementations and original Planning worktree topology.

### [AC-04] Record reproducible performance evidence
- **Given** the same source and interpreter for baseline and optimized fixtures,
- **When** the twelve original fixture consumers run serially and in two reversed-order eight-worker pairs,
- **Then** retained evidence records all samples, selected case identities, pass counts and initialization counts,
  demonstrates fewer repeated initializations, and reports the observed elapsed-time change without a portable
  latency guarantee.

## 5. Assumptions and Invariants

- The optimized scope is the handoff fixture in `packages/devkit-spec/tests/test_integration.py`.
- A module-scoped template is worker-local under pytest-xdist. Initialization under test still runs for each case.
- Copy only a standalone repository with no linked worktree registrations; preserve independent files and symlinks.
- Test-only initialization changes have no production or Living Spec behavior impact; no architectural MUST changes.

## Source feedback

Directly address `FB-handoff-fixture-repeated-preparation`: optimize repeated standalone initialization and verify
isolation and performance. Its completed-state snapshot experiment is evidence, not the implementation design.
`FB-affected-selector-helper-resolution-cost` remains dismissed and outside the implementation scope.
