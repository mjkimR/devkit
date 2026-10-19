---
id: SPEC-summary-length-guard
title: Reject oversized document summaries before creation
summary: "Document creation commands reject summaries longer than 300 characters before writing files, matching the document summary rule."
status: completed
created: 2026-10-19
related_capabilities:
  - CAP-DLV-proposal-incubation
  - CAP-DLV-spec-bundles
related_stories: []
workflow: sdd-spec-bugfix
---

# [SPEC-summary-length-guard] Reject oversized document summaries before creation

## 1. Problem Statement & Motivation

Scaffolding currently accepts summaries that the default document summary rule later rejects, leaving an agent to repair files before committing.

## 2. Defect Characterization

- **Current behavior**: `require_summary` checks emptiness and foreign letters but not length. The originating feedback records PADRs with 309- and 320-character summaries accepted and then refused by `RULE-document-summary`.
- **Expected behavior and its basis**: the document summary rule defaults to at most 300 stripped characters. Creation validation in `CAP-DLV-proposal-incubation` and `CAP-DLV-spec-bundles` must reject longer summaries before writing, with `ARGUMENT_INVALID` targeting `--summary`.
- **Behavior to preserve**: omitted placeholders, stripped nonempty English summaries, empty/non-English refusal, CLI output formats and library error behavior. Existing `test_proposal_summary.py` covers these paths; boundary and no-write checks are missing.
- **Reproduction conditions**: invoke each of `create_spec`, `create_proposal`, and `create_padr` or their CLI commands with a 301-character English summary in a temporary workspace. A PADR uses an existing proposal and a removed empty decisions directory to detect directory creation.
- **Assumptions**: the fixed creation limit is 300 stripped Unicode characters, matching the rule default; project-specific rule settings do not become creation policy. Native Codex orchestration experimentally emulates the managed worker role under explicit user authority and per-command permissions.

## 3. Non-Goals

1. **Scope Excluded**: sentence counting, changes to English detection, configurable creation limits, version bumps, MCP implementation, and orchestration host contracts.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Reject oversized summaries without writes
- **Given** any of the three creation paths and a stripped English summary longer than 300 characters
- **When** creation is requested through the library or CLI
- **Then** `ArgumentError` / `ARGUMENT_INVALID` targets `--summary`, the CLI exits 2, and no file or directory is created.

### [AC-02] Accept the inclusive boundary after stripping
- **Given** a nonempty English summary of exactly 300 characters with surrounding whitespace
- **When** any creation path is requested through the library or CLI
- **Then** creation succeeds and writes exactly the stripped 300-character summary with the existing success output format.

### [AC-03] Preserve existing summary behavior
- **Given** omitted, ordinary valid, empty, or non-English summary input
- **When** existing creation and handoff paths run
- **Then** placeholder/omission behavior, whitespace normalization, valid outputs, handoff preservation, and existing argument refusals remain unchanged.
