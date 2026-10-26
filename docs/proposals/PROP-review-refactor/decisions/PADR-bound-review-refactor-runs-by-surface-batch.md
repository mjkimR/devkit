---
id: PADR-bound-review-refactor-runs-by-surface-batch
title: Bound review-refactor runs by surface batch
summary: For a reviewable review-refactor run, we split the user-selected surfaces into one batch each with its own decision round and defer findings landing on an unselected surface, to keep each round comparable and inside the agreed scope, accepting more rounds per run.
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
mixed diffs that cannot be reviewed as one change. A finding often spans two surfaces, and a change on one surface
carries edits on another (tests, references, documentation).

## 2. Decision Drivers

- Each decision round and each resulting work item stays reviewable by one person.
- Invocation authorizes no change; only the user's decision round does (`ADR-external-playbook-execution`).
- Every finding is decided exactly once, and nothing is applied outside the scope the user agreed.

## 3. Considered Options

- User-selected surfaces and roots split into one batch per surface, one decision round each: reuses the
  `drift-reconciliation` pattern; more rounds per run.
- All surfaces with a top-N cap ranked by maintenance cost: an arbitrary cap over incomparable criteria and large
  mixed diffs.
- Diff-driven since a named ref or the last run: misses accumulated debt; needs `PROP-maintenance-history` without a
  named ref.

## 4. Decision Outcome

- Intake: the user selects the surfaces (code, guidance, CLI) and the roots; missing scope is clarified before the
  review starts. The run splits into batches of one surface each, with one decision round per batch, because each
  round then judges comparable findings.
- A cross-surface finding cites both sides and belongs to the batch of the surface where its change lands, so it is
  decided exactly once.
- A cross-surface finding whose landing surface is outside the selected scope is recorded as deferred with a
  follow-up and is not applied, because the selected surfaces are the run's agreed scope. The user may add that
  surface to the run's scope, which adds its own batch and decision round and is recorded in the run report, because
  that addition is the user's own new authority.
- The edits that follow an agreed change (its tests, the references and documentation naming the changed code, the
  Living Spec statement of the result) belong to that change and its batch on any surface, because a refactor
  changes code, tests and documentation together and splitting them would leave the change inconsistent.

## 5. Consequences

- Positive: each decision round and work item is small and single-surface.
- Negative: a run over three surfaces needs three decision rounds; findings landing on an unselected surface wait
  for a later run unless the user adds that surface.
- Risk: the following-edit rule is stretched to carry an unrelated change on another surface; the diff check of
  each change against its agreed scope bounds it.
- Follow-up: when `PROP-maintenance-history` lands, a diff-driven scope may be offered as an intake option; that
  change needs its own decision.

## 6. Confirmation

- Spec-review checklist of the Development maps intake, per-surface batching and cross-surface assignment (an
  unselected landing surface, the user's scope addition, the edits that follow a change) to playbook sections.
- Fixture exercise records one batch's decision round and its separate change records (proposal section 3).
