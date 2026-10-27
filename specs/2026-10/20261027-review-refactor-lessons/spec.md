---
id: SPEC-review-refactor-lessons
title: 'Review-refactor playbook: parallel application and preservation lessons'
summary: 'Fold the 2026-10-27 code and performance passes into the review-refactor playbook: parallel disjoint-scope application by default, differential preservation evidence, divergence inventories, removal reachability sweeps, an adversarial reviewer brief and a post-integration report update.'
status: in-progress
created: 2026-10-27
related_capabilities:
  - CAP-DLV-review-refactor
related_usecases:
  - UC-review-and-refactor-accumulated-slop
workflow: sdd-spec-feature
---

# [SPEC-review-refactor-lessons] Review-refactor playbook: parallel application and preservation lessons

## 1. Problem Statement & Motivation

Two passes over this repository (the code pass recorded in
`docs/materials/2026-10/20261027-review-refactor-code-pass/report.md` and a performance pass) followed the
`maintenance/review-refactor` playbook and exposed gaps between its procedure and what a large pass needs:

- The playbook applies, verifies and commits agreed changes one after another
  (`ADR-apply-behavior-preserving-batches-as-direct-mode-refactors`). With many independent changes this is too slow;
  both passes ran disjoint changes in parallel worktrees by user decision, outside the written procedure, and hit
  unsynchronized managed assets (a commit made without its checks), result transfer by hand and editing subagents
  that added governance exceptions to make their change pass.
- Tests passing before and after did not catch regressions that a side-by-side comparison of the old and new code on
  the repository's own inputs and edge cases did, or that the fresh reviewer found by constructing inputs (an
  unclosed inline comment hiding later lines; a symlink loop breaking every file listing).
- Consolidating duplicates that behaved differently changed some callers; the playbook has no step to list those
  differences for a decision, and the report has no place for them.
- Removing a path left branches, parameters and types that only the removed path reached; the reviewer found them.
- Stashing to run the old code is unsafe: the stash list is shared by every worktree of a repository.
- The report was written before integration and kept a stale integration state.

## 2. User Stories

- **US-1**: As a user running a broad review-refactor pass, I want agreed independent changes applied in parallel so
  that the pass finishes in a fraction of the sequential time without weaker evidence.
- **US-2**: As a user approving changes, I want each consolidation's behavior differences and each change's
  side-by-side comparison in front of me so that I approve what actually changes.

## 3. Non-Goals

1. **Performance playbook**: a separate maintenance playbook for performance passes is its own proposal.
2. **Handbook**: the release handbook is refreshed at release (`ADR-handbook-on-request-release-snapshot`), not here.
3. **Tooling**: no command or script for differential comparison or worktree fan-out; the playbook states the
   procedure for any repository.
4. **Other parts of the playbook**: intake, batches, review questions, dispositions and contract removals stay as
   they are except where a criterion below names them.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Agreed changes with disjoint write scopes are applied in parallel by default
- **Given** a work item whose agreed changes split into edit tasks with disjoint write scopes and a host that supports
  subagents
- **When** the playbook's agent applies the work item
- **Then** it runs those edit tasks concurrently, each in its own isolated checkout created from the work item's
  current checkpoint and prepared like a fresh checkout of the repository (its setup and managed-asset
  synchronization), with the subagent leaving its result uncommitted
- **And** the playbook's agent moves each result onto the work item branch one at a time, checks its diff against the
  agreed change and its scope, verifies it there and commits it alone through the repository's commit checks, so
  every commit still holds one change with its own evidence
- **And** the work item's final head passes the full verification on a clean tree

### [AC-02] Overlapping scopes and ordering dependencies stay sequential
- **Given** two agreed changes whose write scopes overlap, or one change that builds on another
- **When** the playbook's agent plans the edit tasks
- **Then** it runs them one after another on the previous checkpoint

### [AC-03] Editing subagents never relax governance to make a change pass
- **Given** an editing subagent whose change fails a layering, rule or configuration check
- **When** it would add an exception, an ignore entry, a rule setting or a bypass of the repository's checks
- **Then** the playbook forbids it; the subagent reports the failure and the playbook's agent resolves the placement
  or returns the change to the decision round

### [AC-04] Behavior-preserving changes with a definable input domain record a differential comparison
- **Given** a change that consolidates or replaces a parser, scanner, matcher, file listing, serialized format or
  other function whose inputs can be enumerated or generated
- **When** its preservation evidence is recorded
- **Then** the record includes a comparison of the old and new code on the same inputs (the repository's own corpus
  plus edge cases of the input domain) with the input count and the result, and each difference is either an
  approved behavior change or fixed
- **And** the old code runs side by side from an extracted copy or a separate checkout, never by stashing, because the
  stash is shared by every worktree

### [AC-05] Consolidations list the behavior differences between duplicates for a decision
- **Given** a proposed consolidation of implementations that do not behave identically
- **When** the finding is presented in the decision round
- **Then** it lists each difference with the behavior the consolidation keeps, and the user's decision covers each
- **And** the report records the approved differences under a behavior-changes section, separately from inputs no
  longer accepted

### [AC-06] Removals sweep what only the removed path reached
- **Given** an agreed removal of code
- **When** it is applied
- **Then** the playbook's agent rechecks branches, parameters, types, errors and helpers that only the removed path
  reached, removes those that became unreachable within the agreed change, and records any it keeps or defers

### [AC-07] The fresh reviewer is asked to break the preservation claims
- **Given** a work item ready for review
- **When** the playbook's agent briefs the fresh reviewer
- **Then** the brief gives the reviewer each change's preservation claim and asks for inputs or states under which
  behavior differs, each with a reproduction, plus the list of what it checked and found sound

### [AC-08] The report states the final integration state
- **Given** a run report written before its work item integrates
- **When** the work item integrates or stops
- **Then** the playbook's agent updates the report's outcome with the integration state

## 5. Living Spec Impact

- `CAP-DLV-review-refactor`: change contract (parallel application, governance edits, differential evidence,
  divergence inventory, removal sweep, reviewer brief) and report interface (behavior changes, outcome after
  integration).
- `UC-review-and-refactor-accumulated-slop`: main scenario and extensions for parallel application.
- A new ADR supersedes `ADR-apply-behavior-preserving-batches-as-direct-mode-refactors`, carrying its decision with
  parallel application in place of the one-after-another clause.
