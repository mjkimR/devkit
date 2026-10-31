---
id: SPEC-decision-supersession-check
title: Validate decision supersession consistency
summary: "Report inconsistent whole and partial ADR supersession relationships without automatic edits."
status: planned
created: 2026-10-31
related_capabilities: [CAP-DOCS-document-model, CAP-GOV-spec-rules]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-decision-supersession-check] Validate decision supersession consistency

## 1. Problem Statement & Motivation

`CAP-DOCS-document-model` defines whole and partial decision supersession, but metadata reciprocity relies on
review. Drift previously affected more than twenty ADRs. An agent needs deterministic findings before committing
an inconsistent ledger.

## 2. User Stories

- **US-1**: As an author, I want supersession inconsistencies reported so that whole and partial replacements remain discoverable.

## Source feedback

`FB-decision-supersession-consistency-unchecked`: add report-only checks for ADR status, supersession fields and
partial replacement pointers. Resolve this source only after implementation and verification.

## 3. Non-Goals

1. **Scope Excluded**: Automatic metadata rewriting, decision-graph API changes, PADR validation and semantic judgment of replaced clauses.
2. **Scope Excluded**: New feature dependencies or changes to historical work-unit documents.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Whole replacement status and pointer
- **Given** an ADR with superseded_by on a status other than superseded, or a superseded ADR without a valid superseded_by
- **When** RULE-decision-supersession checks the targeted ADR
- **Then** it reports a non-fixable violation with the field's source line and an actionable remediation.

### [AC-02] Supersedes relationships
- **Given** an ADR naming a missing, ambiguous or non-ADR supersedes target, or a target with neither superseded status nor a partial pointer naming this ADR
- **When** the rule checks the superseder
- **Then** it reports a non-fixable violation; valid whole and partial replacements produce none.

### [AC-03] Partial replacement reciprocity and aliases
- **Given** a visible Superseded in part by code-span ADR pointer
- **When** its target is missing or does not name the earlier ADR in supersedes
- **Then** the rule reports a violation; uniquely resolved aliases on either side match canonical IDs.

### [AC-04] Safe evaluation boundaries
- **Given** valid and invalid ADRs, draft PADRs, masked example pointers and explicit targets or exclusions
- **When** check or fix evaluates the rule
- **Then** only targeted, non-excluded ADRs report findings, historical superseded ADRs remain checked, masked pointers are ignored and no content is rewritten.

## 5. Baseline and Assumptions

At fefc351f the rule is absent and the document model explicitly states review-only enforcement. The before/after
measurement uses a seeded inconsistent pair: no dedicated checker exists at baseline; the delivered rule must
report its inconsistent relationship. Existing index alias resolution remains authoritative. The rule enforces
existing decision-writing requirements and introduces no replacement policy.
