---
id: SPEC-cli-host-lifecycle
title: CLI execution for Host lifecycle operations
summary: "The Host accepts and hands off proposals and integrates verified Development work through CLI operations with source-bound validation. Under ask, the Host carries conversational approval; shared-resource MCP remains available."
status: completed
created: 2026-10-23
related_capabilities:
  - CAP-DLV-proposal-incubation
  - CAP-DLV-human-interaction
  - CAP-INT-mcp-services
  - CAP-MCP-runtime-registration
  - CAP-WT-task-worktrees
  - CAP-COLL-shared-artifacts
related_usecases:
  - UC-incubate-and-hand-off-a-proposal
  - UC-drive-development-to-integration
  - UC-handle-delivery-problems-and-exceptions
workflow: sdd-spec-feature
---

# [SPEC-cli-host-lifecycle] CLI execution for Host lifecycle operations

## 1. Problem Statement & Motivation

Proposal acceptance, Development handoff and final integration depend on lifecycle MCP tools for composed checks and mutations. A Host without those tools can perform only lower-level CLI steps and cannot use the same validated operation boundary. The Host needs one CLI path for each lifecycle action while workers retain MCP access to shared artifacts.

The user approved conversational Host authorization under `ask` in `ADR-host-cli-lifecycle-authority`. The Host presents the exact source, report, target and effects before asking. The CLI revalidates operation identity and policy but does not authenticate the conversational answer. Under `auto`, the CLI derives authority from the retained base configuration. Host command permission remains independent of business approval.

This feature changes the delivery outcomes in `UC-incubate-and-hand-off-a-proposal`, `UC-drive-development-to-integration` and `UC-handle-delivery-problems-and-exceptions`.

## 2. User Stories

- **US-1**: As the Host, I want CLI operations to accept a reviewed proposal and merge its Planning result so that lifecycle execution does not require lifecycle MCP tools.
- **US-2**: As the Host, I want one CLI operation to create the Development worktree and hand off the accepted proposal so that internal checks and mutations stay composed.
- **US-3**: As the Host, I want to integrate a verified Development result through a CLI operation so that local and pull-request routes retain the existing readiness and cleanup protections.
- **US-4**: As the Host, I want to inspect actual Git, worktree and PR state after an unknown result so that I can perform only the remaining validated cleanup.
- **US-5**: As a worker, I want shared artifact and proposal report services to remain available through MCP so that collaboration across worktrees keeps its existing access boundary.

## 3. Non-Goals

- **Scope Excluded**: Approval tokens, signed approval receipts or other infrastructure that authenticates the origin of a conversational answer.
- **Scope Excluded**: A durable recovery journal, daemon, request store or cross-command approval session.
- **Scope Excluded**: Changes to shared artifact identity, retention, publication authority or scope-registry transport.
- **Scope Excluded**: Automatic pull-request integration, new remote-publication authority, host permission changes or removal of the optional MCP runtime.
- **Scope Excluded**: An optional native form path for lifecycle operations after their registrations are removed.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The Host accepts a reviewed proposal through CLI
- **Given** a clean `plan-<slug>` branch whose proposal is at `direction-handoff`, whose `plan-accept` gate is open, and whose report URI is bound to the exact committed source SHA
- **When** the Host invokes `devkit spec proposal accept <slug>` with an explicit `accept_only` or `accept_and_handoff` mode after obtaining the required conversational decision, or when the retained base policy authorizes the operation
- **Then** the command validates the report and workflow readiness, records the accepted status and gate, and merges the checked Planning result through the local route
- **And** `accept_only` does not start Development, while `accept_and_handoff` also starts Development with the selected effort
- **And** success exits `0` and text output reports the accepted proposal and completed effects; `--format json` emits exactly one JSON object

### [AC-02] Handoff starts Development as one composed operation
- **Given** an accepted proposal on the clean base with a recorded `plan-accept` gate and an exact current report URI
- **When** the Host invokes `devkit spec proposal handoff <slug>` after obtaining `proposal-handoff` authority and supplies an effort in `low`, `medium` or `high`
- **Then** the operation creates or validates `dev-<slug>`, runs proposal-to-spec handoff in that worktree, and reports the worktree path, spec bundle and selected effort
- **And** a refused or failed operation preserves the proposal and any created worktree for inspection; it does not silently delete completed effects

### [AC-03] Conversational approval is carried by the Host
- **Given** an operation whose owning policy is `ask`
- **When** the Host executes the command after presenting its exact source, report, target and effects and receiving the user's decision
- **Then** the command requires no interactive stdin, native form, approval token or caller-supplied proof of identity
- **And** the CLI revalidates the operation before mutation, while the Host remains responsible for carrying the user's decision correctly
- **And** workflow guidance distinguishes conversational business approval from host filesystem and tool permission

### [AC-04] Automatic authority is read from the retained base
- **Given** the retained base policy sets the applicable gate to `auto`
- **When** the Host invokes the same CLI operation without a conversational decision
- **Then** the operation proceeds only when the base and prospective result preserve the effective policy and all readiness and identity checks pass
- **And** caller claims, local overlays and host command permission do not grant business authority
- **And** `auto` does not authorize pull-request execution or publication beyond existing policy

### [AC-05] Stale identity or failed readiness refuses mutation
- **Given** a source or report changed after review, an effective policy changed, readiness failed, or a worktree or cleanup identity no longer matches
- **When** the Host invokes the affected operation
- **Then** the command refuses with a stable `UPPER_SNAKE` error code and a deterministic `[ACTION]` directive before the affected mutation
- **And** already completed effects remain visible in the result and are not repeated
- **And** a refusal exits `2`; a negative operation result exits `1`; successful warnings and notices do not change the exit code unless `--strict` is set

### [AC-06] Local and pull-request integration preserve their route limits
- **Given** a verified Development result and an applicable `dev-integration` decision or policy
- **When** the Host invokes `devkit integration integrate <branch>` with route `local` or `pull-request`
- **Then** the local route performs no fetch, push or remote branch deletion, and the pull-request route discloses and validates each remote effect before execution
- **And** required pull-request policy refuses the local route, while automatic pull-request execution remains refused
- **And** both routes preserve source identity, readiness checks, landing validation, integration locking and exact cleanup guards from `ADR-local-and-pull-request-integration`

### [AC-07] Partial or unknown outcomes recover from observed state
- **Given** a local integration fast-forward succeeded but cleanup failed, or the command outcome became unknown
- **When** the Host inspects `devkit worktree status` and the actual Git or PR state, then invokes only the remaining guarded cleanup operation
- **Then** the command does not merge a second time, does not remove an unrelated worktree or branch, and reports each remaining effect
- **And** no request identifier, approval session or recovery state must survive the command process

### [AC-08] Lifecycle MCP registrations are removed while shared MCP remains
- **Given** the local MCP runtime is installed
- **When** its available tools are listed after the change
- **Then** `spec_plan_accept`, `spec_handoff`, `integration_prepare`, `integration_integrate`, `integration_status`, `integration_resume` and `spec_proposal_report_template` are absent
- **And** `spec_proposal_report`, `shared_put`, `shared_get`, `shared_list`, `shared_sweep` and `shared_sweep_apply` remain available under their existing access rules

### [AC-09] CLI output remains agent-first
- **Given** any lifecycle CLI operation
- **When** it succeeds, refuses or returns a partial result
- **Then** stdout contains only the documented result sentinel lines or exactly one JSON object under `--format json`
- **And** advisories use the existing stderr protocol with stable codes and deterministic actions; libraries do not print

## 5. Security, Privacy and Compliance

The Host's conversational decision is the business approval under `ask`; CLI invocation alone does not establish that approval. The CLI does not accept an approval assertion argument. It validates source, report, policy and cleanup identities before each mutation. Native transport permissions and host execution permissions remain separate controls.

The pull-request route uses the existing GitHub adapter and authority boundary. It does not expand publication authority or bypass required checks. Shared artifacts remain data, not instructions or approval credentials, under `CAP-COLL-shared-artifacts`.
