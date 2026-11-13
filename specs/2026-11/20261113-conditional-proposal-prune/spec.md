---
id: SPEC-conditional-proposal-prune
title: Plan proposal cleanup only when applicable
summary: "Omit proposal-prune effects for spec-only activity without proposal history while preserving exact prepared cleanup identity and retry validation."
status: planned
created: 2026-11-13
related_capabilities:
  - CAP-DLV-proposal-lifecycle
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-conditional-proposal-prune] Plan proposal cleanup only when applicable

## 1. Problem Statement & Motivation

`FB-integration-prune-without-proposal` reports a proposal-prune target for a spec-depth Unit that never had a proposal. The no-op makes the integration scope imply missing Planning work. The scoped cleanup extension derives the target from the branch slug alone.

## 2. User Stories

- **US-1**: As an integrating agent, I want only applicable proposal cleanup in the prepared scope so that I can assess the actual effects without investigating a nonexistent proposal.
- **US-2**: As an integrating agent recovering partial cleanup, I want the approved target identity to survive landing and directory removal so that retry validation remains exact.

## 3. Non-Goals

1. **Scope Excluded**: Change integration authority, request persistence, extension protocols, scope cleanup, branch/worktree cleanup or their refusal checks.
2. **Scope Excluded**: Change the standalone prune command or the classic post-finish callback.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Spec-only activity omits proposal cleanup
- **Given** neither pinned source nor pinned target has history for the finished slug's proposal path
- **When** scoped cleanup is prepared, validated and run
- **Then** no proposal-prune target or proposal cleanup notice is produced, and the finished worktree's scope record is still cleaned.

### [AC-02] Proposal history retains cleanup across landing
- **Given** the pinned source or target history includes the finished slug's proposal path, including a handoff that deleted its tracked files
- **When** scoped cleanup is prepared, landed, validated and run again after successful prune or a partial failure
- **Then** its proposal target remains exactly kind proposal-prune, identity docs/proposals/PROP-<slug> and revision source_sha, and empty proposal directories are pruned idempotently.

### [AC-03] Prepared cleanup remains exact
- **Given** a prepared cleanup scope
- **When** a proposal target is added, omitted, duplicated, or has a different identity or source revision, or a scope record revision/namespace changes
- **Then** validation and execution refuse with INTEGRATION_REQUEST_STALE; unknown target kinds retain INTEGRATION_CLEANUP_UNSCOPED.

## 5. Assumptions & Boundaries

Applicability uses committed path history reachable from the request's pinned source_sha or target_sha, rather than mutable directory existence. A historical proposal with the same slug remains applicable because it can leave empty directories. Uncommitted empty directories alone do not establish proposal provenance on the scoped integration path. Git read failures propagate rather than silently omit cleanup. The current IntegrationContext and FinishPlan provide both pinned commits; no shared harness API changes are required.

The behavior restates `CAP-DLV-proposal-lifecycle` and retains the authority and exact-scope contract in `CAP-INT-mcp-services` and the cleanup decision in `ADR-worktrees-and-scope`.

## Source feedback

- `FB-integration-prune-without-proposal`: user-selected direct fix through feedback hygiene, with selection recorded in `MAT-feedback-hygiene-triage`. Resolve only after implementation and verification.
