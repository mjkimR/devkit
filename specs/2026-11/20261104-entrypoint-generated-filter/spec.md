---
id: SPEC-entrypoint-generated-filter
title: Exclude managed outputs from derived entrypoint candidates
summary: "Derives authored code entrypoints while excluding known managed outputs and receipt-owned projected files."
status: in-progress
created: 2026-11-04
related_capabilities: [CAP-TRACE-code-entrypoints]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-entrypoint-generated-filter] Exclude managed outputs from derived entrypoint candidates

## 1. Problem Statement & Motivation

A task boundary includes synchronized outputs as write scope, but those outputs are poor starting points for
reading implementation. Derivation currently offers .claude, .devkit/managed and .devkit/installation.json from
`SPEC-namespace-roadmap`. The filter belongs to derivation; work-scope collection must retain those writes.

## 2. User Stories

- **US-1**: As an agent reviewing derived entrypoints, I want generated-only candidates omitted so that authored
  implementation paths remain the review focus.

## 3. Non-Goals

1. **Scope Excluded**: excluding all ignored paths or entire host directories regardless of ownership.
2. **Scope Excluded**: deleting manual entrypoints, changing scope collection or introducing feature dependencies.
3. **Scope Excluded**: changing how seeded project-owned documents are classified or rewriting the receipt.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Known managed outputs are omitted
- **Given** a boundary naming the managed tree, its descendants and the installation receipt
- **When** derivation runs with or without a receipt
- **Then** those inputs yield no pairs and each has the stable `managed-output` boundary skip reason.

### [AC-02] Receipt ownership distinguishes projections from authored files
- **Given** a valid receipt, projected files, generated-only directories and mixed authored/projected directories
- **When** derivation runs
- **Then** receipt-owned files and generated-only directories are skipped; authored siblings, mixed directories,
  seeded files and ignored authored files remain eligible.

### [AC-03] Explicit selectors cannot restore generated outputs
- **Given** a retained ancestor candidate and a generated descendant
- **When** --code selects the generated file or directory, including --apply
- **Then** the command exits 2 with `SPEC_ENTRYPOINTS_CODE_UNMATCHED` and writes no document; ordinary selectors
  retain their existing behavior.

### [AC-04] Invalid receipts remain actionable
- **Given** a present malformed installation receipt
- **When** derivation runs
- **Then** the typed reader's existing `RECEIPT_INVALID` advisory is propagated with exit 2, instead of silently
  treating the receipt as absent.

### [AC-05] Work scopes retain output paths
- **Given** boundaries naming generated outputs
- **When** shared boundary classification runs for scope collection
- **Then** their normalized code paths remain classified as paths; only derivation adds the ownership filter.

## 5. Baseline & Verification

At input 00511ae149771e6197b51ba52f706992ff272161, deriving `SPEC-namespace-roadmap` through the library reports
managed candidate paths [.claude, .devkit/installation.json, .devkit/managed]. Repeat that exact derivation after
implementation and require an empty managed-candidate set while authored candidates remain.

## Source feedback

`FB-entrypoints-derive-offers-managed-paths`: direct fix for generated-output noise in derivation; resolve only
when implementation, regressions and review verify the complete outcome.
