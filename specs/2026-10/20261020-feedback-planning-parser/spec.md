---
id: SPEC-feedback-planning-parser
title: Clarify Planning execution context and expose reconciliation parsing
summary: "Align Planning context, temporary probe boundaries and reusable reconciliation text parsing."
status: planned
created: 2026-10-20
related_capabilities:
  - CAP-DLV-delivery-workflows
  - CAP-TRACE-code-entrypoints
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-feedback-planning-parser] Planning execution context and reconciliation parsing

## Problem and user stories

Planning workers can read instructions newer than their CLI or cite IDs absent from their branch, and their temporary
probe boundary is unclear. Committed-record consumers also import a private reconciliation parser.
As a Host, I want a consistent Planning context and bounded probes. As a consumer, I want reusable text parsing
without a filesystem snapshot.

## Non-Goals

- Cross-branch ID resolution, worker merge authority, automatic branch refresh, new approval or permission grants.
- Shared scratch services, new parser grammar, compatibility shims or changes to runtime outputs.

## Acceptance Criteria

### [AC-01] Planning depends on newer base documents
- **Given** a Planning branch lacks IDs required from newer main documents.
- **When** the Host prepares or resumes the turn.
- **Then** guidance requires Host refresh before dependent work; a running worker reports the dependency for Host
  recovery without merging or disguising ID references as plain words.

### [AC-02] Instructions and CLI share the assigned context
- **Given** the assigned Planning worktree differs from the entry checkout.
- **When** operational instructions and commands are selected.
- **Then** both resolve from that worktree; needed newer functionality is a Host refresh dependency, not permission
  to fabricate records or mix entry-checkout instructions with the older CLI.

### [AC-03] Temporary Planning probe boundary
- **Given** a Planning probe needs temporary files.
- **When** the Host delegates the turn.
- **Then** it names an ignored probe path within the allowed write scope and worktree; the worker removes temporary
  repositories and files before its last commit, retains evidence in materials, and requests a boundary expansion
  if no permitted path can demonstrate the condition.

### [AC-04] Reusable reconciliation parser preserves behavior
- **Given** reconciliation text and its diagnostic relative path.
- **When** disk bundle loading or committed worker inspection parses targets.
- **Then** both call public parse_targets(text, relative), preserving target order, defaults and invalid-input errors
  without filesystem access inside the parser.

## Assumptions

Host refresh remains subject to existing integration and permission policies. No new decision or ADR is required:
worker Git restrictions and local document resolution remain unchanged.

## Source feedback

- `FB-plan-branch-cannot-reference-main-ids`: direct fix within the four acceptance scenarios above.
- `FB-planning-reverify-worktree-version-skew`: direct fix within the four acceptance scenarios above.
- `FB-planning-probe-lab-location`: direct fix within the four acceptance scenarios above.
- `FB-reconcile-parser-private-reuse`: direct fix within the four acceptance scenarios above.
