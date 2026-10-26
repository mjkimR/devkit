---
id: PADR-apply-approved-contract-removals-as-separate-work-items
title: Apply approved contract removals as separate work items
summary: For unneeded commands, options, public interfaces and compatibility paths found by review-refactor, we let the decision round approve their removal as its own work item with contract and docs updated, to apply reductions without mislabeling contract changes, accepting extra work items.
proposal: PROP-review-refactor
status: draft
created_at: 2026-10-26
---

# [PADR-apply-approved-contract-removals-as-separate-work-items] Apply approved contract removals as separate work items

- **Status**: Draft
- **Date**: 2026-10-26

---

## 1. Context & Problem Statement

The reduction direction (`user`) requires that unneeded commands, options, public interfaces and compatibility paths
can actually be removed. Such a removal changes a contract: callers or inputs that worked stop working. It can never
be presented as behavior-preserving refactoring, and in-repository search does not prove the absence of dynamic or
external consumers. Deferring every such removal leaves reductions as unworked follow-ups.

## 2. Decision Drivers

- Reductions are applied, not left as unworked follow-ups.
- Contract changes stay separate and visible, never mixed into behavior-preserving changes.
- Invocation authorizes no change; only the user's decision round does (`ADR-external-playbook-execution`).

## 3. Considered Options

- The decision round may approve a contract removal as its own work item: applies the reduction, at a second work
  item per removal.
- A contract removal is always a deferred follow-up (feedback or draft proposal): lowest in-run cost, but reductions
  accumulate unworked.
- A removal counts as in-run refactoring when search finds no consumer: lowest cost, but dynamic or external
  consumers the search misses break and a contract change is mislabeled.

## 4. Decision Outcome

- The decision round may approve removing a command, option, public interface or compatibility path, because the
  reduction direction requires applied removals.
- The approved removal becomes its own work item through the repository's normal development workflow, classified
  by that repository's own criteria, with the contract and documentation updated, kept apart from the batch's
  behavior-preserving work item and never routed as a refactor
  (`PADR-apply-behavior-preserving-batches-as-direct-mode-refactors`), because the contract change then stays
  visible and reviewable on its own.
- A compatibility-path removal under the declared compatibility-policy exception (the target repository states that
  no external consumer exists for that package) is a behavior-preserving removal instead; its change record still
  names the inputs or callers no longer accepted.

## 5. Consequences

- Positive: unneeded contracts are removed within the run's authority, each in a reviewable work item.
- Negative: each approved contract removal adds a work item and its contract and documentation updates.
- Risk: an external consumer outside the repository breaks; the contract work item and the named inputs make the
  break traceable.
- Follow-up: none.

## 6. Confirmation

- Spec-review checklist of the Development maps the contract-removal work item and the compatibility-policy
  exception to playbook sections.
