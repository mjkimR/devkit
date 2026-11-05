---
id: SPEC-worker-source-completion
title: Preserve source feedback completion scope
summary: "Worker inspection retains completion scope for explicitly linked feedback that was open at the audit base."
status: completed
created: 2026-11-05
related_capabilities:
  - CAP-DLV-delivery-workflows
related_usecases: []
workflow: sdd-spec-bugfix
---

# [SPEC-worker-source-completion] Preserve source feedback completion scope

## 1. Problem Statement & Motivation

Completing an authorized source feedback file removes it from inferred worker scope and produces a false
outside-scope result. The Host must repeat the complete original grant through explicit scope flags.

## 2. Defect Characterization

- **Current behavior**: `derive_scope` only admits source feedback with status `open` at returned HEAD.
  Accepted input `00511ae149771e6197b51ba52f706992ff272161` has an open source; returned head
  `a07e64096f359b96245421f2f60b47877f945fb9` resolves it and drops the exact path from inferred scope.
- **Expected behavior and its basis**: `CAP-DLV-delivery-workflows` source-feedback completion and
  `ADR-feedback-lifecycle-ledger` permit an authorized direct fix to resolve its source. Inspection must retain
  that completion path. Clarify the capability's head-only scope description to recognize this transition.
- **Behavior to preserve**: Open returned-head sources remain admitted. Sources already terminal at audit base,
  unrelated sources, identity changes and other terminal transitions gain no implicit completion scope.
  Explicit scope still replaces the entire inferred scope. Missing or ambiguous head sources retain their errors.
- **Reproduction conditions**: Commit linked external feedback as open, then commit its resolution and a worker
  envelope. Inspect using the open commit as audit base with no boundary for that file.

## 3. Non-Goals

1. **Scope Excluded**: New CLI flags, stored authorization records, source renames/deletions, broader terminal
   editing permissions, scope-extension policy changes or unrelated worker refactoring.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Retain an open source's completion path
- **Given** an explicitly linked feedback ID at the same exact path is open at the audit base
- **When** the returned head resolves that source and worker inspection derives scope
- **Then** scope includes the path with source `source-feedback` and its ID, and no outside-scope finding names it.

### [AC-02] Exclude non-completion terminal edits
- **Given** a source is already terminal, missing, unknown or has another ID at the audit base
- **When** the returned head edits that source in a terminal state
- **Then** no implicit completion scope is added; an existing explicit boundary remains independent.

### [AC-03] Preserve existing scope semantics
- **Given** an open returned-head source, an unrelated source, an ambiguous source or an explicit scope override
- **When** worker inspection runs
- **Then** existing open-source inclusion, unrelated-source exclusion, ambiguity errors and full-replacement override
  behavior remain unchanged; inspection preserves Git HEAD and worktree state.

## 5. Source feedback

`FB-worker-inspect-resolved-source-scope`: direct fix of audit-base completion inference and its completion record.

## 6. Assumptions

The audit base supplied or derived by inspection is the comparison's accepted starting snapshot. Only an
`open` to `resolved` transition at the same path and ID adds completion scope. No architectural invariant or
lasting authorization policy changes, so no ADR is required. Development effort is medium for independent review.
