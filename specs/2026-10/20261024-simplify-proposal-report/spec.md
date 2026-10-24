---
id: SPEC-simplify-proposal-report
title: Simplify proposal review report template
summary: Reduce mandatory report sections to three core sections and simplify PADR decision fields for concise approval briefings
status: planned
created: 2026-10-24
related_capabilities:
  - CAP-DLV-proposal-incubation
related_usecases:
  - UC-incubate-and-hand-off-a-proposal
workflow: sdd-spec-feature
---

# [SPEC-simplify-proposal-report] Simplify proposal review report template

## 1. Problem Statement & Motivation

Proposal review reports published via `devkit spec proposal report` currently require 8 mandatory H2 sections and 4 H4 sub-headings for each PADR. Much of this content (listing envelope filenames, repeating effort levels, and writing placeholder text for unverified areas or waived findings) is mechanical validation metadata rather than human-decision evidence. This creates overly long and cluttered briefings that hinder fast, clear user approval decisions.

The report template needs to be simplified to focus on the 3 core decision-making elements: the overall Outcome, key architectural Decisions (Problem and Choice), and the Proposed approval effects. Mechanical metadata and conditional observations should be optional or streamlined.

## 2. User Stories

- **US-1**: As a developer/agent reviewing a proposal, I want a concise proposal review report with only 3 mandatory sections (Outcome, Decisions, Proposed approval effects) so that approval briefings are clear and fast to read.
- **US-2**: As an agent publishing a report, I want PADRs to require only Problem and Choice fields without forcing Rejected alternatives or Consequences headers so that PADR summaries remain compact.
- **US-3**: As a system consumer, I want `devkit spec proposal report --template` and its validation to enforce the streamlined structure while preserving language parity (en/ko) and backward compatibility for `planning_support`.

## 3. Non-Goals

- **Scope Excluded**: Changing the shared artifact storage format or hashing scheme.
- **Scope Excluded**: Removing PADR identity tracking (every committed PADR must still be accounted for).
- **Scope Excluded**: Altering CLI command arguments for `devkit spec proposal report` or `devkit spec proposal accept`.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Streamlined Mandatory Sections
- **Given** a clean proposal commit and a review report body
- **When** the report is checked or published via `devkit spec proposal report`
- **Then** validate only 3 mandatory H2 sections: `Outcome` (결론), `Decisions` (결정), and `Proposed approval effects` (제안된 승인 효과)
- **And** `Boundary impacts`, `Planning effort and support`, `Open decisions and waived findings`, and `Unverified areas` are optional rather than required.

### [AC-02] Compact PADR Fields
- **Given** a proposal with committed PADRs
- **When** the `Decisions` section is validated
- **Then** every committed PADR must still be accounted for as an H3 header
- **And** require only `Problem` (문제) and `Choice` (선택) as mandatory fields per PADR; `Rejected alternatives` and `Consequences` are optional.

### [AC-03] Development Effort in Approval Effects
- **Given** a proposal with a declared `dev_effort`
- **When** `Proposed approval effects` is validated
- **Then** the section must identify the recommended `dev_effort`
- **And** separate mandatory sections for `Recommended Development effort` and envelope filename coverage checks are removed.

### [AC-04] Template and Helper Compatibility
- **Given** a request for `devkit spec proposal report <slug> --template`
- **When** the template is generated
- **Then** emit the concise 3-section layout in the workspace language (`en` or `ko`) with compact PADR fields
- **And** `planning_support()` safely returns the planning effort/support details from the optional section if present, or falls back to `planning_effort` metadata / effects summary without crashing.
