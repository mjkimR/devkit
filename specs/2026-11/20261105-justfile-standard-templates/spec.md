---
id: SPEC-justfile-standard-templates
title: Minimal Command Setup Guidance
summary: Improves onboarding examples and proposes opt-in catalog instructions for creating only the justfile, CLI and MCP entry points a project needs.
status: planned
created: 2026-11-05
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-justfile-standard-templates] Minimal Command Setup Guidance

## 1. Problem Statement & Motivation

Handed off from proposal PROP-justfile-standard-templates on 2026-11-05.
- Target Docs Blueprint: `PROP-justfile-standard-templates-target` (Living Spec targets for this plan and reconcile.md)

### 1. Background & Hypothesis

Pilot adoption found friction choosing verification entry points. The existing installation guide already
inspects justfile, Makefile, package scripts and CI and connects selected fast commands to `verify-commands`.
CAP-GATE-commit-gates already runs project commands independently of their language.

The retained onboarding scope is concrete examples that reuse those commands and optionally show a small
justfile for a project without a command interface. Non-Python setup examples from
PROP-multi-runtime-project-harness belong here.

A related design candidate is an opt-in instruction bundle in `devkit-catalog` for creating or extending
justfile, CLI and MCP interfaces. Its primary purpose is to prevent unnecessary commands and registrations
at creation time. The existing `maintenance` review-refactor playbook handles cleanup of existing interfaces.

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Minimal Command Setup Guidance so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Technical Spike Questions

- Which pilot repository and native verification command provide the first representative onboarding example?
- What is the smallest instruction set that controls new entry points without duplicating `cli-tool`'s Python
  implementation rules, `harness` consumption guidance or the review-refactor playbook?
- Should the catalog candidate use one conditional instruction or separate justfile, CLI and MCP instructions?
  Select a bundle name and asset layout in Planning; do not add an always-loaded command inventory.

### 3. Proposed Design & Impact

#### Retained onboarding scope

- Reuse existing repository commands and document their working directory and prerequisites.
- Provide an optional `test`, `fix`, `verify` example only where a project needs a new task interface.
  These names are examples, not a required recipe schema.
- Keep per-commit verification fast; leave slow suites in the project's full verification path.
- Avoid repeating checks already run by existing hooks or the built-in `rules-check` gate.
- Explain non-Python onboarding using native project commands through the existing gate.

#### Catalog instruction candidate

- Start with the concrete operations and callers a project needs, then add only entry points serving them.
- Prefer an existing command over another wrapper or alias with the same purpose. Add a separate entry point
  when it has a distinct caller, execution constraint or useful task-level composition.
- Register MCP tools only for operations that need MCP access; do not mirror every CLI command automatically.
- Keep common help and setup guidance short; make specialized details discoverable when the task needs them.
- Load the instruction when creating, configuring or extending these interfaces, not on every task.
- Treat removal of an existing public command as a compatibility decision; use review-refactor for cleanup.

Planning settles whether the catalog candidate warrants a bundle and defines its final scope.

#### Non-Goals

- No scaffold CLI, runtime detector, adapter framework or justfile merge engine.
- No mandatory task runner or fixed recipe names.
- No automatic `just verify` gate selection based on the presence of a justfile.
- No automatic command deletion, MCP filtering engine or usage telemetry.

### 4. Validation

Walk through a repository with existing commands and one without a task interface. Confirm that the selected
commands exist, execute from the documented directory and do not duplicate hook checks. Verify a representative
non-Python example without adding a runtime adapter.

For the catalog candidate, review creation scenarios for justfile, CLI and MCP: each exposed operation must
have an identified use, existing commands must be reused where suitable, and instructions must not prescribe
unsupported framework-specific behavior. Run catalog manifest checks if that candidate is retained.

