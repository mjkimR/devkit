---
id: SPEC-response-style-survey
title: Apply the accepted response style
summary: "Deploys conclusion-first replies with arrow-marked core sentences, preserved content and format exceptions, and rendered conversation language."
status: in-progress
created: 2026-10-20
related_capabilities:
  - CAP-DIST-content-packages
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-response-style-survey] Apply the accepted response style

## 1. Problem Statement & Motivation

Apply the accepted direction from `ADR-response-style-adaptive-replies`,
`ADR-response-style-guidance-budget`, `ADR-response-style-measurement` and
`ADR-response-style-source-selection`. The current skill imposes fixed block and sentence counts;
the accepted style uses a conclusion-first opening and marked conclusions with necessary explanation.
`MAT-response-style-rewrite-draft` and `MAT-response-style-measurement-design` retain the authored
examples and the limits of their evidence.

## 2. User Stories

- As a reader, I want the answer and its qualifications early, with enough explanation for my request.
- As a bundle consumer, I want the same opted-in style deployed with my configured language and native projections.

## 3. Non-Goals

- Scope Excluded: live model generation, benchmarks, scoring, universal quality claims and compaction experiments.
- Scope Excluded: shared guidance-limit changes, skill-body size limits, new presets, host variants and report schemas.
- Scope Excluded: edits to accepted ADRs or historical survey materials.

## 4. Acceptance Criteria & Behavioral Contracts

### Scenario 1 [AC-01]: Ordinary replies preserve meaning and explain conclusions

- **Given** an ordinary reply governed by the skill,
- **When** its instructions are reviewed against the authored scoped-fact and explanation examples,
- **Then** they require a conclusion-first sentence, `→ **Core sentence.** Supporting explanation` points,
  blank lines between points, required facts and qualifications, and requested depth without fixed block or sentence counts.

### Scenario 2 [AC-02]: Required formats and work reports remain complete

- **Given** an artifact-only request, a required workflow format or an unfinished task,
- **When** the skill and authored artifact/status examples are reviewed,
- **Then** required formats and fields take precedence, artifacts have no conversational framing, and reports
  distinguish completed scope from remaining work with actual verification and material limitations.

### Scenario 3 [AC-03]: Language and deployment remain portable

- **Given** the opt-in response-style bundle with `auto` or `ko` language,
- **When** bundle deployment tests and consumer smoke run,
- **Then** the rendered skill has the selected language instruction, explicit user language overrides,
  deliverable-language requirements and short Korean wording guidance, with no unresolved Jinja and existing native projections intact.

### Scenario 4 [AC-04]: Guidance remains a bounded pointer

- **Given** the single guidance fragment,
- **When** its UTF-8 bytes including LF are counted and the bundle is deployed,
- **Then** it is at most 300 bytes, points to the skill and summarizes the ordinary format, and introduces no skill-body limit.

## 5. Assumptions and premises

The target bundle, language branches, catalog tests and consumer smoke exist on the handoff base.
The measurement material is named `response-style-measurement-design.md`; the shortened handoff filename
refers to that preserved document. No interface or boundary change is needed. The authored examples establish
reviewable intent, not measured model behavior. Host integration refreshes the installed receipt and projections.
There are no explicitly linked source feedback IDs to resolve.
