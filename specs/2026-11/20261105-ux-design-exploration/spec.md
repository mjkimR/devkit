---
id: SPEC-ux-design-exploration
title: Add an explicitly invoked UI/UX improvement skill
summary: "Ship uiux-improve as an opt-in content-only skill that carries requested interface and flow improvements through the consumer workflow with optional local perspectives."
status: planned
created: 2026-11-05
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-ux-design-exploration] Add an explicitly invoked UI/UX improvement skill

## 1. Problem Statement & Motivation

An explicitly invoked design entry should improve a supplied interface or user flow through actual changes and
appropriate verification. Independent design, unusual directions, reference research and criticism can help when
selected for concrete assignments. They do not require a fixed cast or an alternatives-only final report.

The accepted direction is recorded in `ADR-uiux-improvement-workflow-boundary`. The target blueprint is
`PROP-ux-design-exploration-target`. Implementation stays within the consumer's existing delivery workflow.

## 2. User Stories

- **US-1**: As a product developer, I want an optional overall UI/UX improvement entry so that design work can
  reach requested changes and representative usage checks.
- **US-2**: As an agent user, I want selected local roles and focused returns so that unrelated tasks receive no
  design-role metadata and small requests remain inexpensive.
- **US-3**: As a consumer maintainer, I want ordinary catalog installation without a required delivery package so
  that my existing workflow and authority remain in control.

## 3. Non-Goals

- **Scope Excluded**: Consumer product screens, new browser/design tools, runtimes, dependencies or delivery workflows.
- **Scope Excluded**: General design ideation, automatic sibling skill invocation and persistent role memory.
- **Scope Excluded**: Comparative-effectiveness experiments, mandatory audits, numeric scores, fixed casts or iteration quotas.
- **Scope Excluded**: Global specialist registration, always-loaded design guidance or changes to consumer policy.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Explicit opt-in distribution

- **Given** installed catalog bundles without a uiux-improve selection,
- **When** the consumer synchronizes and then explicitly selects uiux-improve:core,
- **Then** no UI/UX assets exist before selection and the entry plus four local role files deploy afterward,
  with user-only invocation metadata on supported projections and no global specialist agents.

### [AC-02] Overall improvement and narrower requests

- **Given** a supplied interface or flow and the requested outcome,
- **When** the coordinator follows the entry,
- **Then** the instructions lead from focused inspection through coherent design, requested implementation under
  the existing workflow and actual verification; a review-only request ends with findings and no product edits.

### [AC-03] Proportionate optional perspectives

- **Given** an improvement request of any size,
- **When** the coordinator chooses useful perspectives,
- **Then** the guidance permits inline completion, optional research and critique, zero critic findings and no
  fixed alternatives or role count; independent first passes receive no peer conclusions.

### [AC-04] Context, tools and authority

- **Given** a selected role assignment or unavailable interaction/delegation tool,
- **When** the coordinator dispatches or verifies work,
- **Then** it passes the resolved absolute local role path, bounded facts/actions and a stop condition, preserves
  existing permissions and workflow approvals, and reports actual checks and unavailable coverage without claiming
  native isolation or independent contexts that the host did not provide.

### [AC-05] Self-contained original guidance

- **Given** a dist/catalog-only consumer without the authoring repository's documents,
- **When** the installed entry and references are read,
- **Then** their local links resolve without authoring-repository IDs, sibling bundle requirements or copied
  upstream prose; original guidance includes practical flow and visual lenses with contextual examples.

### [AC-06] Installed consumer lifecycle

- **Given** built dist/catalog wheels in an isolated environment without spec, docs or agt packages,
- **When** the public CLI selects, removes and reselects uiux-improve,
- **Then** the entry and local roles deploy and remove independently, user-owned design artifacts survive and
  selection does not start work or alter the development approach.

## 5. Assumptions

- The settled name is uiux-improve. Public naming is reversible; no competing installed entry exists.
- This delivery authors an agent skill, not product screens, so no Screens section or UX object register applies.
- Tool and semantic checks establish packaging and instruction consistency, not aesthetic or team superiority.
- The new bundle is not selected in this repository; its discovery registration is tested with explicit consumer selection.
- No numeric before/after outcome is required; the accepted direction excludes an effectiveness benchmark.
