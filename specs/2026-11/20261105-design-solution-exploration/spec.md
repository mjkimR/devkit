---
id: SPEC-design-solution-exploration
title: Add an explicitly invoked general design ideation skill
summary: "Add an opt-in general solution design skill with optional local roles, distinct mechanisms and conversation-first results."
status: planned
created: 2026-11-05
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-design-solution-exploration] General solution exploration

## 1. Problem Statement & Motivation

Architecture, data models, module boundaries and processing or development workflows benefit from exploring
materially different mechanisms while preserving the actual goal and hard constraints. The accepted direction
in `ADR-explicit-solution-exploration` is an explicitly invoked, independent content-only skill.
`PROP-design-solution-exploration-target` names the retained document targets.

## 2. User Stories

- As a developer, I want useful design directions with mechanisms, benefits, tradeoffs and decision-changing
  assumptions so I can choose an approach without starting implementation or a validation program.
- As a consumer agent, I want optional local roles and an honest inline fallback so simple questions stay small
  and separate contexts are used only when useful and supported.

## 3. Non-Goals

**Scope Excluded**: UI/UX-specific ideation, business brainstorming, automatic implementation, mandatory research
reports, fixed casts or option counts, scores, consensus, persistent memory, creativity benchmarks, A/B or
comparative-team validation, new runtime code, dependencies, feature edges and global specialist registration.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Opt-in self-contained distribution
- **Given** dist and catalog are installed without delivery packages or companion selections
- **When** the consumer selects the design-explore core preset and synchronizes
- **Then** one user-only skill, three local role files and two references deploy; no global specialist or ambient
  design instruction deploys; before selection the skill is absent and the development approach is unchanged.

### [AC-02] General design mechanisms and preserved constraints
- **Given** a general architecture, model, module or workflow design problem
- **When** the coordinator explores it
- **Then** instructions recover the actual goal and hard constraints, distinguish mechanisms from brand/name
  variants, and return useful directions with benefits, tradeoffs and decision-changing assumptions without
  requiring a fixed count, score, consensus or comparative-effectiveness experiment.

### [AC-03] Optional roles and independent first passes
- **Given** separate exploration or evidence can change the result
- **When** the coordinator selects local role assignments
- **Then** absolute role paths resolve from the invoked skill; payloads state premises, facts, permissions,
  boundaries, stop condition and expected return; supported fresh contexts omit peer conclusions on first passes;
  unavailable fresh contexts use a disclosed inline fallback; missing roles remain missing coverage.

### [AC-04] Conversation-first result and bounded authority
- **Given** exploration is invoked with or without an output destination
- **When** the coordinator synthesizes actual returns
- **Then** plausible unusual mechanisms retain their differences; conversation is the default; only the coordinator
  writes an explicitly requested destination; roles write no retained files, product source, index or HEAD;
  invocation confers no implementation, commit, approval or publication authority; refusals are not bypassed.

### [AC-05] Optional bounded research and criticism
- **Given** evidence or critique can change a consequential design choice
- **When** the coordinator uses a researcher or critic
- **Then** inspected evidence, inference and unknowns remain distinct; criticism permits zero findings and a bounded
  refinement pass; no survey, prototype, benchmark or benefit-proof program becomes a prerequisite.

### [AC-06] Independent removal and installed consumer lifecycle
- **Given** a built-wheel consumer has selected design-explore alongside another opt-in bundle
- **When** it removes and re-adds design-explore
- **Then** only owned design-explore assets retire and return; user artifacts and the other bundle survive;
  sync --check passes without devkit-agt, devkit-docs or devkit-spec.

## 5. Assumptions and measurement

- Current base includes the separately landed research and UI/UX bundles. Their paths and behavior are preserved.
- Reuse one solution-explorer role with distinct premises rather than separate personality roles, because mechanism
  differences carry the useful variation. Reference research and criticism remain optional.
- No product screen changes; conversation output needs no UX document.
- Measure distribution availability at the accepted handoff head with this change disabled: entry-point count,
  source presence and local-role count; repeat after implementation and verify installed selection/removal.
  This verifies availability and ownership, not design quality, creativity or team superiority.
- No upstream text is copied; original guidance avoids additional license or attribution obligations.
