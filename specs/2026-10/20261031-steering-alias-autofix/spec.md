---
id: SPEC-steering-alias-autofix
title: Fix aliases in steering citations and glossary owners
summary: "Rewrite uniquely resolved aliases in steering code-span citations and glossary Owner cells while preserving surrounding content."
status: planned
created: 2026-10-31
related_capabilities: [CAP-GOV-spec-rules]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-steering-alias-autofix] Fix aliases in steering citations and glossary owners

## 1. Problem Statement & Motivation

`RULE-document-reference` fixes aliases in quick references but leaves steering citations and glossary Owners for
manual correction. Extend its existing deterministic alias repair to these ID-free inputs.

## 2. User Stories

- **US-1**: As an agent renaming a document, I want one rules fix to update steering citations and glossary Owners,
  so a later check reports only references that require a decision.

## 3. Non-Goals

1. **Scope Excluded**: Changing ID indexing, reference graphs, handoff resolution, canonical glossary bracket
   formatting, document layout, or files outside the rule's existing steering/Owner inputs.
2. **Scope Excluded**: Guessing missing or ambiguous targets, or adding cross-feature dependencies.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Steering citation aliases
- **Given** a visible single-code-span alias in a targeted steering file that resolves uniquely
- **When** the rule checks and then fixes the file
- **Then** the finding is fixable and only the alias ID is replaced with its canonical ID; a second fix changes no file.

### [AC-02] Glossary Owner aliases
- **Given** aliases in backtick or bracket references of the Owner column in a recognized root glossary table
- **When** the rule fixes the glossary
- **Then** it replaces only each uniquely resolved alias ID, preserving delimiters, whitespace and other cells.

### [AC-03] Scope and uncertainty
- **Given** masked citations, excluded or untargeted files, missing/ambiguous IDs, canonical IDs, or bracket IDs outside Owner cells
- **When** the rule checks or fixes steering inputs
- **Then** the existing report scope remains unchanged and none of those spans are rewritten.

### [AC-04] Snapshot and stable documents
- **Given** valid steering input and its alias declaration in a rule cache snapshot
- **When** the rule fixes through its cache
- **Then** it uses snapshot content, keeps steering files outside the document index and reference graph, and converges to no alias findings.

## Source feedback

`FB-steering-citations-not-fixable`: cover steering code-span citations and root glossary Owner aliases.

## Baseline and assumptions

At 7e0f153d, the existing rule tests demonstrate both input kinds remain unchanged under fix. Retain those
fixtures with updated expectations and add coverage for bracket Owners, masking, uncertainty, targeting and idempotency.
The recommended implementation preserves bracket delimiters in Owner cells; canonical bracket formatting is unchanged.
