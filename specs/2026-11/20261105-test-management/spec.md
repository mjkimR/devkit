---
id: SPEC-test-management
title: Evidence-based test management playbook
summary: "An opt-in maintenance playbook assesses consumer test coverage, resource isolation and runner configuration while preserving native verification and approval boundaries."
status: in-progress
created: 2026-11-05
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-test-management] Evidence-based test management playbook

## 1. Problem and User Stories

As an AI coding agent, I need to assess a selected suite without imposing one repository's test tiers, parallel
runner or branch policy on another. Planning evidence is retained under
`docs/materials/2026-11/20261105-test-management/`; `PROP-test-management-target` defines the target documentation.

## 2. Non-Goals

- **Scope Excluded**: consumer edits, tier migration, new runtime commands/selectors, application bug repair,
  CI/branch policy redesign, mandatory history, source snapshots and a benchmark framework.

## 3. Acceptance Criteria

### [AC-01] Opt-in selection and deployment
- **Given** the catalog maintenance bundle is available.
- **When** a consumer selects testing, all, an existing individual preset, or no maintenance preset.
- **Then** testing/all deploy the complete three-file playbook, existing individual presets keep their asset sets,
  and unselected consumers receive no playbook; selection/retrieval invokes no assessment.

### [AC-02] Prerequisites precede execution
- **Given** a suite has executable collection hooks, shared services or unavailable socket support.
- **When** the agent assesses it.
- **Then** the agent inspects prerequisites before execution and reports missing required checks as not_run;
  directory/marker labels do not establish resource safety or completed coverage.

### [AC-03] Decision and workflow boundaries
- **Given** an invoked assessment with proposed configuration changes.
- **When** it reaches its one decision round.
- **Then** an unattended run applies nothing and approved candidates name exact scope and use the consumer's normal
  development/review/integration process; assessment grants no CI or branch-policy change authority.

### [AC-04] Native consumer contracts
- **Given** the three inspected repositories and a labelled non-pytest example.
- **When** the agent walks through the shipped procedure.
- **Then** it preserves their command/resource/completion boundaries and uses the non-pytest example's native
  runner without installing pytest; walkthrough evidence states expected and observed actions and limitations.

### [AC-05] Conditional runner guidance
- **Given** a pytest tuning request or inconclusive measurement.
- **When** the agent reads conditional runner guidance.
- **Then** it compares collected identities, outcomes/skips, cleanup and elapsed time under one revision/lock/set,
  reports unexecuted work as not_run, retains defaults on inconclusive results and imposes no universal worker/time
  setting or application-specific fixture.

### [AC-06] Self-contained packaging and documentation
- **Given** the shipped playbook and retained scenario records.
- **When** deployment, reference and relevant project checks run.
- **Then** conditional references resolve, files fit asset budgets, catalog documentation and reciprocal capability/
  use-case contracts agree, and related tests/lint/types/rules pass; phrase checks alone are not procedural proof.

## 4. Assumptions

Use the approved three-file design and testing preset; no runtime architecture or dependency edge changes.
Author-led walkthroughs validate instructions, not live application behavior or performance. Reference repositories
remain read-only. Existing maintenance history is independently opt-in and is not extended by this unit.
