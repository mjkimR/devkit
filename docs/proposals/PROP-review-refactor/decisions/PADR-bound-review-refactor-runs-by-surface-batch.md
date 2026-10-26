---
id: PADR-bound-review-refactor-runs-by-surface-batch
title: Bound review-refactor runs by surface batch
summary: For a reviewable review-refactor run, we split user-selected surfaces into one batch each with its own decision round, which may approve contract removals as separate work items, and allow batch-scoped subagents, to keep each round small, accepting more rounds per run.
proposal: PROP-review-refactor
status: draft
created_at: 2026-10-26
---

# [PADR-bound-review-refactor-runs-by-surface-batch] Bound review-refactor runs by surface batch

- **Status**: Draft
- **Date**: 2026-10-26

---

## 1. Context & Problem Statement

A review-refactor run covers code, agent guidance and CLI commands, whose review criteria differ and whose findings
are not comparable on one scale. A run over everything at once produces a decision round too large to judge and
mixed diffs that cannot be reviewed as one change. The reduction direction (`user`) also requires that unneeded
commands, options and public interfaces can actually be removed; such a removal changes a contract and can never be
presented as behavior-preserving refactoring. A broad review is parallelizable per root or module, but parallel
reviewers over-report and must not acquire decision or write authority.

## 2. Decision Drivers

- Each decision round and each resulting work item stays reviewable by one person.
- Invocation authorizes no change; only the user's decision round does (`ADR-external-playbook-execution`).
- Contract changes stay separate from behavior-preserving changes.
- Reductions are applied, not left as unworked follow-ups.
- Parallel review shortens a broad pass without weakening evidence or authority.

## 3. Considered Options

- **Bounding**: user-selected surfaces and roots split into one batch per surface, one decision round each (reuses
  the `drift-reconciliation` pattern; more rounds per run); all surfaces with a top-N cap ranked by maintenance cost
  (arbitrary cap over incomparable criteria, large mixed diffs); diff-driven since a named ref or the last run
  (misses accumulated debt; needs `PROP-maintenance-history` without a named ref).
- **Contract removals**: the decision round may approve one as its own work item (a second work item per removal);
  always a deferred follow-up (reductions accumulate unworked); in-run refactoring when search finds no consumer
  (dynamic or external consumers break, and a contract change is mislabeled).
- **Parallel review**: the playbook's agent reviews alone (slow on broad scope); spawned subagents per root, module
  or verification task, with the playbook's agent keeping coordination, the decision round and integration
  (faster, needs a validation step).

## 4. Decision Outcome

- Intake: the user selects the surfaces (code, guidance, CLI) and the roots; missing scope is clarified before the
  review starts. The run splits into batches of one surface each, with one decision round per batch, because each
  round then judges comparable findings.
- A cross-surface finding cites both sides and belongs to the batch of the surface where its change lands, so it is
  decided exactly once.
- The decision round may approve a contract removal (command, option, public interface or compatibility path). It
  becomes its own work item through the repository's development workflow, with the contract and documentation
  updated, kept apart from the batch's behavior-preserving work item, because the reduction direction requires
  applied removals and the contract change stays visible.
- Within a batch, the playbook uses spawned subagents when they shorten the pass and the host supports them: for
  example parallel review per root or module, or independent verification of a consolidation or removal. The
  playbook's agent keeps coordination, the decision round and integration. Without subagent support the same steps
  run in the playbook's agent.
- A subagent's result is an evidence-backed opinion. The playbook's agent validates every finding and verification
  claim against the code or the diff at the cited location before it enters the decision round or a change record;
  an unconfirmed claim is dropped or recorded as a coverage gap. Subagents never ask the user, approve a change or
  write the run's records.
- A subagent's write scope stays inside its batch: review and verification subagents change nothing, and a subagent
  that applies an agreed change writes only the paths of that batch's work item.

## 5. Consequences

- Positive: each decision round and work item is small and single-surface; removals are applied with their contract
  change visible; broad passes run in parallel without new authority.
- Negative: a run over three surfaces needs three decision rounds; each contract removal adds a work item.
- Risk: subagents over-report; the validation step and the named-cost rule bound it, at the cost of re-reading each
  cited location.
- Follow-up: when `PROP-maintenance-history` lands, a diff-driven scope may be offered as an intake option; that
  change needs its own decision.

## 6. Confirmation

- Spec-review checklist of the Development maps intake, per-surface batching, cross-surface assignment, the
  contract-removal work item and the subagent rules (validation, no decision authority, batch write scope) to
  playbook sections.
- Fixture exercise records one batch's decision round and its separate change records (proposal section 3).
