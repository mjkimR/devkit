---
id: SPEC-compact-integration-approval
title: Compact native integration approval
summary: "Optimize all four integration MCP tools with one native confirmation, concise scope and result output, and explicit detailed inspection."
status: completed
created: 2026-10-18
related_capabilities:
  - CAP-INT-mcp-services
  - CAP-HARN-agent-guidance
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-compact-integration-approval] Compact native integration approval

## 1. Problem Statement

The integration MCP tools expose the entire internal request in the native approval form and every result.
Guidance asks for conversational approval before the native form and requires a redundant prepare call.
Optimize prepare, integrate, status and resume together while retaining exact internal scope binding and recovery.

## 2. User Story

As an agent and reviewer, I want one concise integration confirmation and bounded tool results so that I can
understand effects, inspect details when needed and recover partial execution without approving twice.

## 3. Non-Goals and Assumptions

- **Scope Excluded**: Removing internal validation, changing readiness providers, durable requests, new host adapters,
  automatic integration dispatch, new network operations, or changing host permission approval policy.
- **Assumptions**: Native form approval satisfies local dev-integration ask; conversational approval remains for CLI
  fallback. All four tools return compact output by default; status alone offers detail=true for retained internals.
  Keep structured and text JSON compatibility; reduce the shared payload rather than drop either transport encoding.

## 4. Acceptance Criteria

### [AC-01] Native confirmation shows effects and binds full internal scope

- **Given** a committed ready branch and its planned cleanup
- **When** integration_integrate is called directly
- **Then** exactly one form shows repository, full source/target commits, worktree and branch removal choices, exact
  cleanup target identities, local FF method and network exclusion; filesystem identities, policy hashes, evidence
  and implementation registrations are absent from the form; approval defaults false and changed scope still blocks.

### [AC-02] Every MCP tool has a compact default result

- **Given** prepare, integrate, status or resume
- **When** a tool returns a retained request result
- **Then** it includes request ID/digest, concise effect scope, status, authority, steps, errors and notices without
  internal filesystem identities, policy hashes, provider evidence, repeated finish data or empty optional fields.

### [AC-03] Details and partial recovery stay available

- **Given** a retained request, including a partial integration
- **When** integration_status is called with detail=true
- **Then** the complete original request, evidence, cleanup revisions and observed state are available; compact partial
  results keep failing operation, observed state, errors and steps; resume finishes only approved remaining scope
  without another form, and a prepared or declined request cannot be resumed as approved.

### [AC-04] Guidance routes directly to one native approval

- **Given** MCP integration is available under ask policy
- **When** the agent finishes checks and presents the verified change report
- **Then** guidance routes directly to integration_integrate without a separate chat approval or mandatory prepare;
  prepare is optional read-only inspection, status handles inspection, and resume handles already approved recovery.
  Unavailable native confirmation retains the explicit conversational approval and CLI fallback.
