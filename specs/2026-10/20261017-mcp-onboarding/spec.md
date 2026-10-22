---
id: SPEC-mcp-onboarding
title: Explicit MCP onboarding and registration status
summary: "Add explicit Codex MCP setup and registration diagnostics, connected to installation guides without implicit sync registration."
status: completed
created: 2026-10-17
related_capabilities:
  - CAP-HOST-lifecycle-observation
  - CAP-INT-mcp-services
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-mcp-onboarding] Explicit MCP onboarding and registration status

## 1. Problem Statement & Motivation

The server and configuration generator exist, but installation does not lead an agent to registration.
An explicit setup command should register a retained runtime and a status command should distinguish
registration from a working connection and visible approval UI.

## 2. User Stories

- **US-1**: As an installing agent, I want discoverable, repeatable MCP registration so that native integration
  tools can become available without changing host settings during ordinary synchronization.

## 3. Non-Goals

1. **Scope Excluded**: Automatic registration or host CLI execution during sync; a persistent MCP selection setting.
2. **Scope Excluded**: Other host adapters, project-scoped configuration editing, trust or permission changes.
3. **Scope Excluded**: Starting a persistent server, proving current-session connection or approval UI from a CLI.
4. **Scope Excluded**: Changing this development session's actual MCP registration while implementing the feature.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Explicit registration and repeat execution

- **Given** Codex is available and the retained runtime contains the MCP SDK and devkit server
- **When** setup runs with --host codex from a retained base checkout
- **Then** it registers user-scoped server devkit through Codex CLI, verifies the result, returns action registered,
  and an identical enabled registration returns action unchanged without writing.

### [AC-02] Existing registration conflict

- **Given** devkit is registered with a different command, arguments, environment, cwd, tool restrictions or disabled state
- **When** setup runs
- **Then** it refuses with HOST_MCP_REGISTRATION_CONFLICT before mutation unless --replace was explicitly supplied;
  replacement uses Codex add and verifies the result without first removing the existing entry.

### [AC-03] Registration diagnostics

- **Given** a desired runtime and workspace
- **When** status runs with --host codex
- **Then** it reports missing, matching or different registration, the desired command and arguments, SDK availability,
  user registration scope, and connection/UI/trust/permission evidence as unknown; exit is 0 for matching with SDK,
  1 for missing/different registration or missing SDK, and 2 when inspection cannot run.

### [AC-04] Runtime and host failures

- **Given** a missing SDK, unavailable/failing Codex, invalid host response, or linked-worktree base/runtime
- **When** setup runs
- **Then** it returns a stable advisory with exit 2 before registration for preflight failures; a failed add or verification
  reports the failure without claiming success or removing registrations; status remains read-only.

### [AC-05] Output and onboarding

- **Given** new, existing or already installed repository onboarding
- **When** the installation instructions are followed
- **Then** they link an optional Codex MCP setup route covering the extra, user scope, retained base/runtime,
  conflict handling, status, removal, client reconnect and separate UI verification. CLI JSON is exactly one object,
  text results are sentinels, and subprocess output never leaks into result streams.

### [AC-06] Project configuration does not authorize hidden user writes

- **Given** the workspace or an ancestor declares a project-level devkit MCP entry
- **When** status or setup runs, including setup with --replace
- **Then** status distinguishes user registration state and effective workspace state; setup refuses with
  HOST_MCP_REGISTRATION_SHADOWED before mutation, preserving both configuration files even for a matching project entry.

## 5. Assumptions

Codex is the only implemented adapter. The existing fixed server name devkit and Codex's user-scoped CLI registration
are retained; switching repositories is an explicit conflict. Setup uses the running Python, requiring invocation
from the retained environment. A differing entry needs --replace; identical entries preserve all settings.
Sync remains independent of machine registration. No recurring sync diagnostic is added without an explicit
project selection contract. Codex's own configuration writer owns persistence; devkit does not edit TOML or trust.
