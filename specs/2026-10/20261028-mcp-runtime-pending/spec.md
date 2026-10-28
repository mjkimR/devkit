---
id: SPEC-mcp-runtime-pending
title: Remove speculative MCP registration notices from general status
summary: "Remove MCP_REGISTRATION_PENDING from general status while preserving actual registration planning and locked sync's withheld-write notice."
status: in-progress
created: 2026-10-28
related_capabilities:
  - CAP-MCP-runtime-registration
  - CAP-DIST-sync-and-transactions
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-mcp-runtime-pending] Remove speculative MCP registration notices from general status

## 1. Problem Statement & Motivation

General status infers desired registration from provider metadata and local ownership without loading the provider.
A provider may return `None` or report an unavailable runtime, so this inference gives unsupported retry advice.
`ADR-remove-speculative-mcp-status-notice` settles removal of that inference and preservation of actual-plan diagnostics.

## 2. User Stories

- **US-1**: As an agent inspecting checkout health, I want general status to omit speculative MCP advice and explicit registration operations to report their actual results.

## 3. Non-Goals

- **Scope Excluded**: Runtime cache, TTL, fingerprint, observation state, replacement readiness checks, runtime provider changes, registration schema changes and unrelated status refactoring.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Provider-free general status

- **Given** absent provider, provider returning `None`, runtime-unavailable provider or provider desiring a real missing registration, with and without an installation receipt
- **When** general status runs
- **Then** it returns no `MCP_REGISTRATION_PENDING`, loads no provider, invokes no runtime probe, writes no registration state and inspects no registration ownership ledger or destination solely for that check.

### [AC-02] Explicit registration planning

- **Given** the four provider outcomes from AC-01
- **When** actual registration planning or registrations-only sync runs
- **Then** the outcomes remain no-provider no-op, no desired registration for `None`, `MCP_RUNTIME_UNAVAILABLE` warning and concrete registration plan/action respectively. Existing explicit MCP setup/status, provider failures and reconciliation refusals remain unchanged.

### [AC-03] Locked sync withheld writes

- **Given** a fresh checkout whose actual registration plan has a host state of `write`
- **When** locked sync leaves that registration unwritten
- **Then** it returns `MCP_REGISTRATION_PENDING` with fix `uv run devkit sync --registrations-only` and writes no host entry. Absent provider, `None` and runtime-unavailable outcomes produce no invented pending notice and preserve their actual no-op or warning.

### [AC-04] Independent status diagnostics

- **Given** independent core, host-hook or gate-health findings
- **When** general status runs
- **Then** those findings retain existing reporting and exit semantics, with no replacement MCP readiness check.

### [AC-05] Consistent documentation

- **Given** the MCP capability, distribution capability and distribution quick reference
- **When** the change is reconciled
- **Then** they consistently distinguish provider-free general status from explicit registration diagnosis and locked sync's concrete withheld-write notice, without an observation-state contract.

## 5. Verification and assumptions

Use fake providers and isolated Git fixtures; never install a runtime or mutate real host files.
Measure before/after with the missing-registration test at handoff head `5c8150d16a1a42b73036d99f93f9ff8ced9573b3` and its delivered counterpart: baseline general status reports one pending notice; head reports zero; locked sync retains one in both.
The proposal premises agree with the current base: only dist's general-status inference changes.
No deferred scope remains from the withdrawn observation design.

## Source feedback

`FB-mcp-registration-pending-ignores-runtime` is promoted and terminal. Its reference supplies traceability; this Development turn does not edit or resolve it.
