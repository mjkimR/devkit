---
id: SPEC-verification-execution-ownership
title: Separate Host and worker verification execution ownership
summary: "Define worker-native synchronous verification and Host-owned post-integration asynchronous execution, with portable client adoption guidance that preserves existing verification contracts."
status: planned
created: 2026-11-10
related_capabilities: [CAP-HARN-agent-guidance, CAP-DLV-delivery-workflows, CAP-DLV-test-management]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-verification-execution-ownership] Verification execution ownership

## 1. Problem Statement & Motivation

Host-only asynchronous verification instructions are reachable through common completion guidance and ambiguous
repository-wide instructions. A Development worker therefore launches a second fixed-commit execution checkout
inside its task, although its assigned worktree can run native checks synchronously. Client-owned instructions
can retain the same ambiguity after managed assets are upgraded.

## 2. User Stories

- As a worker, I run the required native checks in my assigned worktree and return their evidence.
- As a local-orchestrated Host, I retain integrated-result asynchronous execution and final coverage responsibility.
- As a client maintainer, I update ambiguous instructions without changing my native verification contract.

## 3. Non-Goals

1. **Scope Excluded**: CLI role/cwd restrictions, execution runtime changes, new policy/configuration schemas.
2. **Scope Excluded**: removing required checks, mandatory new test tiers, automatic edits to client-owned guidance.
3. **Scope Excluded**: blanket worker E2E or devkit execution requirements for direct/session and cloud PR work.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Worker and common guidance preserve native verification
- **Given** local and cloud rendered worker, completion and payload instructions,
- **When** a worker follows its ordinary Development task,
- **Then** native checks run synchronously in its assigned worktree, necessary selective E2E remains supported,
  and it does not inherit Host exec launch/wait/cleanup or integrated-result responsibility.

### [AC-02] Host owns integrated asynchronous execution
- **Given** local-orchestrated Host guidance and the repository AGENTS instructions,
- **When** independent required asynchronous coverage is selected after landing,
- **Then** the Host owns fixed-SHA launch, collection, cleanup and final coverage; applicability follows the actor,
  not the current directory; direct/session work does not inherit that procedure.

### [AC-03] Portable client adoption preserves requirements
- **Given** the client guide and maintenance execution recommendations,
- **When** adopting the responsibility split in a project with native combined checks or without E2E/devkit,
- **Then** existing commands, prefixes, coverage and CI remain; no new tier or split is required; managed sync and
  manually owned AGENTS changes are distinguished and existing explicit instructions are preserved.

### [AC-04] Rendered assets and routing are regression checked
- **Given** the source and rendered local/cloud assets,
- **When** the relevant bundle tests and rules run,
- **Then** tests verify worker/Host ownership, conditional completion routing and payload boundaries while retaining
  existing asynchronous result/coverage contracts; all checks exit 0.

### [AC-05] Living Spec and client entrypoints agree
- **Given** capabilities, the ownership decision and installation entrypoints,
- **When** independently reviewed against the changed assets,
- **Then** each affected contract reflects the responsibility split and links the portable client guide; no runtime
  execution restriction or automatic client migration is claimed.

## 5. Assumptions

The user-approved worker-native execution rule takes precedence over inherited ambiguous AGENTS text for this run.
No timing improvement is claimed. Host execution policy and final required coverage stay in force.
