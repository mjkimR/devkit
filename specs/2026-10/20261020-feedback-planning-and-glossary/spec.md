---
id: SPEC-feedback-planning-and-glossary
title: Clarify proposal decomposition recovery and validate glossary owners
summary: Keep decomposition in Backlog with actionable Planning return guidance and validate Owner IDs in the repository glossary.
status: completed
created: 2026-10-20
related_capabilities:
  - CAP-DLV-proposal-incubation
  - CAP-GOV-spec-rules
  - CAP-DOCS-document-model
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-feedback-planning-and-glossary] Planning recovery and glossary Owner checks

## Problem and user stories

Agents need actionable recovery when decomposition is requested during Planning, and a check for dangling glossary
Owner references. As an agent, I want the existing Backlog restriction explained and glossary owners validated
without inventing a document identity for the glossary.

## Source feedback

- `FB-decomposed-from-refused-during-planning`: clarify return to Backlog and decomposition-specific advice.
- `FB-glossary-owner-ids-unchecked`: validate references in the root glossary Owner column.

## Non-Goals

- **Scope Excluded**: in-Planning decomposition, new provenance fields, new approval policy or automatic branch cleanup.
- **Scope Excluded**: general ID-free document indexing, glossary document kinds, naming checks, required owners,
  automatic repairs, package glossary expansion and edits to pre-existing terminal feedback.

## Acceptance Criteria

### [AC-01] Refused decomposition gives a usable recovery
- **Given** a parent with a local or fetched Planning branch, or a non-draft parent.
- **When** a child is created with --decomposed-from.
- **Then** SPEC_PROPOSAL_IN_PLANNING remains the error, no child or parent is changed, and advice describes a
  Host-managed return to draft Backlog, preserving evidence and removing Planning branches after authorized integration;
  it never recommends retrying decomposition on the plan branch. An editable draft still creates its child.

### [AC-02] The complete Planning return is documented
- **Given** a Planning run determines it must decompose.
- **When** the executor follows Planning and Backlog guidance.
- **Then** it preserves materials, closes pending questions and commits draft plus needs_decompose before returning;
  the Host obtains existing integration authority, integrates the committed return, removes local/fetched Planning
  branch blockers within existing authorization, and checks Backlog editability before creating children.
  Changing status alone grants no decomposition, merge or deletion authority.

### [AC-03] Glossary Owner references resolve uniquely
- **Given** docs/glossary.md with a five-column Term/Definition/Owner/Avoid/Code identifiers table.
- **When** RULE-document-reference checks that file through the workspace cache.
- **Then** each full ID in backticks or brackets in an Owner cell must resolve to exactly one indexed document;
  unresolved or ambiguous IDs produce error violations at their source line, without autofix or indexing the glossary.

### [AC-04] Glossary checking stays narrow and targeted
- **Given** prose, other cells, code examples, comments, escaped text, empty owners or other ID-free documents.
- **When** the rule runs, including a targeted or snapshot run.
- **Then** it checks only visible Owner ID references in recognized root glossary tables, reports only targeted files,
  respects cache exclusions and leaves existing indexed-document checks and fixes unchanged.

## Assumptions

The existing five-column header defines the supported table. Empty/non-reference owners remain allowed; this is
reference resolution, not table-schema or naming enforcement. The root glossary alone is the approved extension.
Existing return-to-Backlog policy remains authoritative; no accepted MUST or approval rule changes.
