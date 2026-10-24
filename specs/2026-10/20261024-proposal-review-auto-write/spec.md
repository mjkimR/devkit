---
id: SPEC-proposal-review-auto-write
title: Publish proposal review before acceptance
summary: Publish one source-bound proposal review before plan-accept, avoid composing it during acceptance, and configure automatic publication in the project settings.
status: planned
created: 2026-10-24
related_capabilities: [CAP-DLV-proposal-incubation]
related_usecases: [UC-incubate-and-hand-off-a-proposal]
workflow: sdd-spec-feature
---

# [SPEC-proposal-review-auto-write] Publish proposal review before acceptance

## 1. Problem Statement & Motivation

Proposal review uses a source-bound report stored through the shared artifact adapter. Report authoring and publication belong before `plan-accept`; repeating them during acceptance duplicates work and can create multiple reports for the same proposal revision. Project settings also need to control whether the agent automatically writes and publishes that report.

## 2. User Stories

- **US-1**: As a project maintainer, I want the proposal review report written once before acceptance so that acceptance consumes the reviewed report without composing or publishing another one.
- **US-2**: As a project maintainer, I want to enable or disable automatic proposal review report publication in `.devkit/config.toml` so that the workflow follows project preference.

## 3. Non-Goals

1. **Scope Excluded**: Changing the source-bound report schema, its validation rules, shared artifact storage contract, or lifecycle approval authority.
2. **Scope Excluded**: Generating semantic review conclusions in deterministic application code; the agent remains responsible for report content.
3. **Scope Excluded**: Allowing `plan-accept` without a valid report for the exact reviewed source.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Automatic report publication happens before acceptance
- **Given** a proposal is ready for `plan-accept` and `[tool.spec.proposal_review].auto_write` is `true` or omitted
- **When** the Planning agent finishes reviewing the committed proposal revision
- **Then** it writes and publishes one complete source-bound report through the shared adapter before presenting the acceptance request
- **And** the acceptance request carries that report's exact URI and source SHA
- **And** acceptance validates and consumes that report without composing or publishing another report

### [AC-02] Automatic publication can be disabled
- **Given** `[tool.spec.proposal_review].auto_write` is `false`
- **When** the proposal reaches `plan-accept`
- **Then** the agent does not automatically write or publish a report
- **And** the acceptance flow requires a report published explicitly before acceptance and consumes its exact URI without publishing another report

### [AC-03] Proposal review configuration is validated and exposed
- **Given** `.devkit/config.toml` contains `[tool.spec.proposal_review] auto_write`
- **When** `devkit spec policy` reads the effective project policy
- **Then** it reports the effective boolean value, with omitted `auto_write` defaulting to `true`
- **And** a non-boolean value or an unknown key fails with `SPEC_CONFIG_INVALID` and identifies the invalid setting

### [AC-04] Stale and missing reports remain refused
- **Given** the report is missing, invalid, or bound to a different committed source SHA
- **When** acceptance validates the report URI
- **Then** acceptance is refused without writing or publishing a report
- **And** the result directs the agent to publish a valid report before requesting acceptance
