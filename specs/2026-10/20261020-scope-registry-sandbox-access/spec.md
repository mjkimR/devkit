---
id: SPEC-scope-registry-sandbox-access
title: Side-effect-free work scope registry queries
summary: "Keep shared Git-directory storage while making record and history queries side-effect-free, with shared reader locking and explicit mutation permissions."
status: planned
created: 2026-10-20
related_capabilities:
  - CAP-COLL-work-scope-registry
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-scope-registry-sandbox-access] Side-effect-free work scope registry queries

## 1. Problem Statement & Motivation

Queries currently create namespace directories, open locks for writing, and clean interrupted record and token
files. Sandboxes protecting Git administration therefore require write authorization for logical reads.
`ADR-keep-shared-storage-and-separate-read-access` selects shared reader locks without relocation.

## 2. User Stories

- As an agent in a linked worktree, I want to query registered scopes and history with read access so that I can
  inspect overlaps without authorizing registry mutations.

## 3. Non-Goals

- **Scope Excluded**: MCP, storage relocation, permission provisioning, sandbox settings, new policy configuration,
  changing mutation authorization, remote filesystems, Windows locking, or core lock API changes.
- **Scope Excluded**: treating an empty or partially readable registry as proof that active work has no overlap.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Queries never mutate filesystem state
- **Given** absent or populated state, optional own tokens, and interrupted record/token temporary files,
- **When** ordinary query, query --spec, or query --history executes,
- **Then** it performs no mkdir, writable open, creation, unlink, cleanup, or journal append; files and entries remain
  unchanged and existing records, ownership indicators, overlap results and history retain their output contracts.

### [AC-02] Namespace errors remain observable
- **Given** an absent namespace or an existing namespace with a missing, unreadable, symlink or nonregular lock,
- **When** query or history accesses it,
- **Then** only actual namespace ENOENT yields empty results; existing namespace lock failures return
  SPEC_SCOPE_SHARED_PATH_UNAVAILABLE, including FIFO rejection without a blocking open. Permission failures never
  become empty success. Invalid record and journal warnings remain visible.

### [AC-03] Readers and writers synchronize on the existing lock
- **Given** a regular non-symlink namespace lock and concurrent writers,
- **When** a query or history read runs,
- **Then** it opens the existing lock read-only, holds shared flock across enumeration and reading, excludes writers
  using exclusive flock on the same inode, and preserves SPEC_SCOPE_TIMEOUT and SPEC_SCOPE_LOCK_UNSUPPORTED.
  Record and journal queries are separate observations. An absent observation may precede initial registration.

### [AC-04] Mutation and repository identity stay intact
- **Given** a base checkout, two linked worktrees and an unrelated repository,
- **When** registration, update, release and stale sweep execute,
- **Then** linked worktrees share records and overlaps, the unrelated repository remains isolated, ownership and
  revision checks persist, and mutation paths retain interrupted-file cleanup and explicit write permissions.
  Configured absolute shared_path and namespace overrides keep their meaning.

### [AC-05] Platform and sandbox evidence
- **Given** available macOS and Linux runtimes and an initialized registry in protected Git administration,
- **When** compatibility and sandbox smoke checks execute,
- **Then** actual execution verifies read-only-fd shared flock against exclusive writers on both platforms, and
  ordinary, --spec and --history queries succeed without escalation on this host. Setup may use scoped approval;
  success grants no mutation permission or guarantee about other hosts. Unavailable required execution remains open.

## 5. Assumptions and Handoff Premises

The handoff's localfs wrapper, token cleanup and CLI ownership paths match the current base. The accepted ADR and
comparison remain applicable; no boundary expansion is needed. Keep cleanup opt-in at query ownership lookup while
preserving existing mutation defaults. No source feedback items were linked. The separate MCP follow-up remains
`PROP-worker-shared-state-mcp`; it is outside this implementation.
