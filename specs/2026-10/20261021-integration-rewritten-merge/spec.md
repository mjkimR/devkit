---
id: SPEC-integration-rewritten-merge
title: Preserve integration cleanup after metadata-only merge rewrites
summary: Track the verified post-hook merge identity while preserving provenance, content, policy and cleanup guards.
status: completed
created: 2026-10-21
related_capabilities:
  - CAP-INT-mcp-services
  - CAP-WT-task-worktrees
related_stories: []
workflow: sdd-spec-bugfix
---

# [SPEC-integration-rewritten-merge] Preserve integration cleanup after metadata-only merge rewrites

## 1. Problem Statement & Motivation

Integration cleanup retains a pre-hook merge SHA even when a post-merge hook replaces that commit with identical content and parents. The source remains integrated, but cleanup incorrectly reports a stale request.

## 2. Defect Characterization

- **Current behavior**: `_land` records the built result before `fast_forward`; Git executes post-merge hooks before returning, while cleanup validates ancestry of the original result. An amended merge is not its ancestor.
- **Expected behavior and its basis**: `CAP-INT-mcp-services` permits guarded cleanup after verified local integration. Adopt the observed result only when its tree and ordered parents equal the checked commit, retaining all other request guards.
- **Behavior to preserve**: source identity, source containment, policy checks and result ancestry during resumed cleanup under `CAP-WT-task-worktrees`; ordinary merges, ff-only and later descendant commits remain supported.
- **Reproduction conditions**: an integration fixture installs an executable post-merge hook that amends only the commit message. Run the integration regression test with pytest before the production fix.

## 3. Non-Goals

1. **Scope Excluded**: changing hooks, gate behavior, PR landing rules, general rewrite equivalence, or weakening source and ancestry guards.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Metadata-only replacement permits cleanup
- **Given** a checked local merge and a post-merge hook that changes its message while preserving its tree and ordered parents
- **When** integration lands and observes the replacement
- **Then** it records the replacement SHA and completes cleanup without a second authorization.

### [AC-02] Unchecked structural changes preserve the task
- **Given** a hook that changes result content or ordered parents
- **When** integration observes the replacement
- **Then** it reports a stale request and does not remove the task worktree or branch.

### [AC-03] Request guards remain effective
- **Given** source or effective policy mutation during landing
- **When** integration proceeds toward cleanup
- **Then** existing request validation refuses cleanup and preserves the task.

### [AC-04] Ordinary and resumed cleanup remain supported
- **Given** an unchanged landing or a verified metadata replacement with an interrupted cleanup
- **When** cleanup runs or resumes with unchanged authority and descendant target history
- **Then** cleanup completes using the recorded landed identity and existing ancestry checks.

## Assumptions

Message, author and committer metadata may differ; equal tree and ordered parents establish the bounded equivalence. This applies only immediately after the executor's local fast-forward, never to arbitrary replacements discovered on resume.

## Source feedback

`FB-integration-cleanup-stale-after-merge-rewrite` is the directly addressed source. Its external location is outside this worker's write boundary; the Host owns disposition after verified results.
