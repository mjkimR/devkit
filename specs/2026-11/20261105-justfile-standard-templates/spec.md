---
id: SPEC-justfile-standard-templates
title: Minimal Command Setup Guidance
summary: "Provides opt-in creation-time guidance for justfile, CLI and MCP entry points with native verification setup examples."
status: active
created: 2026-11-05
related_capabilities: [CAP-DIST-content-packages, CAP-GATE-commit-gates]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-justfile-standard-templates] Minimal Command Setup Guidance

## 1. Problem and User Stories

As an agent configuring a project, I need to expose only useful commands and tools from the start, reuse existing
commands and select fast commit checks. Existing-interface cleanup belongs to review-refactor.

## 2. Non-Goals

- **Scope Excluded**: scaffold CLI, runtime detection/adapters, mandatory task runners, automatic gate selection,
  deletion of existing commands, MCP filtering engines and usage telemetry.

## 3. Acceptance Criteria

### [AC-01] Opt-in catalog instruction
- **Given** devkit-catalog is installed.
- **When** `command-design` is selected.
- **Then** its `core` preset deploys one conditional instruction with no always-loaded guidance or native skill;
  without selection it deploys nothing.

### [AC-02] Creation-time decisions
- **Given** an agent creates or extends a justfile, CLI or MCP interface.
- **When** it follows the instruction.
- **Then** each added entry point names an operation and caller, suitable existing commands are reused, MCP does
  not automatically mirror the CLI, and specialized help is loaded on demand. Preserve public compatibility;
  existing-interface cleanup is separate. The instruction is self-contained and framework-independent.

### [AC-03] Onboarding examples
- **Given** a project with existing native verification commands or one without task recipes.
- **When** the agent follows the setup guide.
- **Then** it can explicitly configure an existing fast command without a runtime adapter, or optionally compose
  only the recipes it needs. Examples distinguish fast commit checks from full verification and avoid duplicate
  `rules-check` execution. Recipe names and justfile presence never auto-configure gates.

## 4. Assumptions

Use the bundle name `command-design` and one instruction: the decision criteria are shared across the three
interfaces, so separate assets would repeat them. The actual pilot repository was not provided; verify a small
Node example fixture and label it as an example, not as pilot evidence. No interactive UI is added.
