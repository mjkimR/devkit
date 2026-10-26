---
id: PADR-bound-review-refactor-runs-by-surface-batch
title: Bound review-refactor runs by surface batch with batch-scoped subagents
summary: For a reviewable review-refactor run, we split user-selected surfaces into one batch each with its own decision round and use read-only, batch-scoped subagents whose claims the playbook's agent validates, to keep each round small and fast, accepting more rounds per run.
proposal: PROP-review-refactor
status: draft
created_at: 2026-10-26
---

# [PADR-bound-review-refactor-runs-by-surface-batch] Bound review-refactor runs by surface batch with batch-scoped subagents

- **Status**: Draft
- **Date**: 2026-10-26

---

## 1. Context & Problem Statement

A review-refactor run covers code, agent guidance and CLI commands, whose review criteria differ and whose findings
are not comparable on one scale. A run over everything at once produces a decision round too large to judge and
mixed diffs that cannot be reviewed as one change. A broad review is parallelizable per root or module, but parallel
reviewers over-report and must not acquire decision or write authority.

## 2. Decision Drivers

- Each decision round and each resulting work item stays reviewable by one person.
- Invocation authorizes no change; only the user's decision round does (`ADR-external-playbook-execution`).
- Parallel review shortens a broad pass without weakening evidence or authority.

## 3. Considered Options

- **Bounding**: user-selected surfaces and roots split into one batch per surface, one decision round each (reuses
  the `drift-reconciliation` pattern; more rounds per run); all surfaces with a top-N cap ranked by maintenance cost
  (arbitrary cap over incomparable criteria, large mixed diffs); diff-driven since a named ref or the last run
  (misses accumulated debt; needs `PROP-maintenance-history` without a named ref).
- **Parallel review**: the playbook's agent reviews alone (slow on broad scope); spawned subagents per root, module
  or verification task, with the playbook's agent keeping coordination, the decision round and integration
  (faster, needs a validation step).

## 4. Decision Outcome

- Intake: the user selects the surfaces (code, guidance, CLI) and the roots; missing scope is clarified before the
  review starts. The run splits into batches of one surface each, with one decision round per batch, because each
  round then judges comparable findings.
- A cross-surface finding cites both sides and belongs to the batch of the surface where its change lands, so it is
  decided exactly once. A cross-surface finding whose landing surface is outside the selected scope is recorded as
  deferred with a follow-up and never applied in the run, because adding an unselected batch would expand scope
  without authority.
- Within a batch, the playbook uses spawned subagents when useful and the host supports them: for example parallel
  review per root or module, or independent verification of a consolidation or removal, because parallel review
  shortens a broad pass. The playbook's agent keeps coordination, the decision round and integration, because
  authority stays with the user's decision round. Without subagent support the same steps run in the playbook's
  agent.
- A subagent's result is an evidence-backed opinion. The playbook's agent validates every finding and verification
  claim against the code or the diff at the cited location before it enters the decision round or a change record;
  an unconfirmed claim is dropped or recorded as a coverage gap. A verification or negative-reachability claim enters
  a change record only with its commands and results, which the playbook's agent re-runs before recording; a root
  counts as covered only when the subagent's result lists what it read. This keeps evidence unweakened by parallel
  review. Subagents never ask the user, approve a change or write the run's records.
- A subagent's write scope stays inside its batch: playbook-spawned subagents do review and verification only,
  read-only. The routed development workflow owns the applying step; a subagent applies an agreed change only as a
  worker that workflow assigns, under its write boundaries and sequencing, so no change bypasses the workflow's
  reviews and gates.

## 5. Consequences

- Positive: each decision round and work item is small and single-surface; broad passes run in parallel without new
  authority or write access.
- Negative: a run over three surfaces needs three decision rounds; findings landing on an unselected surface wait
  for a later run.
- Risk: subagents over-report; the validation step, the command re-run and the named-cost rule bound it, at the
  cost of re-reading each cited location and re-running verification.
- Follow-up: when `PROP-maintenance-history` lands, a diff-driven scope may be offered as an intake option; that
  change needs its own decision.

## 6. Confirmation

- Spec-review checklist of the Development maps intake, per-surface batching, cross-surface assignment (including an
  unselected landing surface) and the subagent rules (validation and re-run, no decision authority, read-only scope,
  the fallback on a host without subagents) to playbook sections.
- Fixture exercise records one batch's decision round and its separate change records (proposal section 3).
