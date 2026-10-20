---
id: PROP-scope-registry-sandbox-access
title: Work scope registry access across sandboxed worktrees
summary: "Compare Git-directory storage, shared devkit state, and MCP-mediated access for the work scope registry across sandboxed worktrees. Define permission boundaries and query behavior without assuming that relocating state removes approval requirements."
status: accepted
created_at: 2026-10-20
target_area: collaboration/
priority: medium
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/scope/
    - packages/devkit-spec/src/devkit_spec/cli/scope.py
    - packages/devkit-spec/tests/scope/
    - docs/capabilities/collaboration/
  excludes:
    - Git internals and host-wide sandbox policy
    - General-purpose agent scratch storage
task_kind: feature
workflow: sdd-proposal
---

# [PROP-scope-registry-sandbox-access] Work scope registry access across sandboxed worktrees

## 1. Background & Hypothesis

`CAP-COLL-work-scope-registry` stores the shared registry below the Git common directory and each worktree's
ownership token in its own Git directory. The common directory gives every linked worktree the same registry
without separate path configuration, while individual Git directories separate ownership tokens.

The registry's `query` operation acquires an exclusive file lock and uses the common operation wrapper, which
creates the namespace directory when needed and cleans interrupted-write temporary files. Consequently, a logical
read can require filesystem writes. A sandbox that protects `.git` can refuse the query before any records are
read. An observed invocation returned `SPEC_SCOPE_SHARED_PATH_UNAVAILABLE` for the namespace's `.lock`; the same
query succeeded after command-scoped escalation and returned zero registered records. This was a sandbox write
failure, not an automatic approval-review denial. An empty registry does not establish that active work has no
overlap.

Moving files into `.devkit` would separate devkit state from Git internals, but each worktree has its own `.devkit`
and a shared path may still be outside another agent's writable roots. An MCP service could own the filesystem
access, but its server permissions, tool authorization and lifecycle would still need explicit design.

Hypothesis: an explicit registry access boundary can preserve cross-worktree coordination with narrowly scoped
permissions. Planning should determine whether the operational benefit justifies changing storage or transport,
using the current Git-directory implementation with scoped escalation as the baseline.

## 2. Technical Spike Questions

- **Q1 — Shared location and identity:** How do base and linked worktrees discover one registry without confusing
  different clones? Compare Git common-directory discovery, a shared `.devkit/state/` location and a service-owned
  registry. Account for a moved or removed base checkout and simultaneous sessions.
- **Q2 — Permission provisioning:** What exact filesystem paths and operations does each alternative require?
  Determine how worktree preparation could supply only the required access. Treat sandbox refusal, approval-review
  denial and missing host capabilities as distinct outcomes; do not assume that a path outside `.git` is authorized.
- **Q3 — Query semantics:** Can querying existing or absent state avoid file creation and temporary-file cleanup?
  Establish the consistency tradeoff under concurrent registration, update and release before recommending a
  lock-free, shared-lock or separately maintained read path.
- **Q4 — Ownership and durability:** Where do per-worktree tokens live, how are they protected, and how are stale
  records recovered? `shared_path` currently relocates only the registry, not the tokens. Define persistence across
  agent sessions and safe cleanup without treating coordination records as disposable scratch files.
- **Q5 — MCP feasibility:** Can the available host expose bounded registry operations with appropriate authorization,
  concurrency and error reporting? Compare server startup, availability and maintenance cost with direct CLI access;
  define behavior when the service is unavailable without silently widening permissions.

## 3. Proposed Design & Impact

Recommend retaining Git common-directory discovery, registry storage and per-worktree tokens, and separating
read access from mutation. `PADR-keep-shared-storage-and-separate-read-access` records the direction; the comparison
and verification design are in `materials/access-comparison.md`. This recommendation awaits plan acceptance.

Both ordinary `query` (including `--spec`) and `query --history` MUST perform no filesystem mutation: no directory
or lock creation, writable opens, journal append, token cleanup or interrupted-record cleanup. Ownership lookup
MUST read tokens without cleanup. Mutating callers retain cleanup and current ownership/revision checks.

For an existing namespace, open its existing regular, non-symlink `.lock` read-only and take a shared flock with
the existing deadline. Writers continue using the same inode and exclusive flock. Hold the reader lock across
record enumeration and reads, or journal reads, preserving namespace-consistent observations relative to writers. Record and journal operations remain separate
observations, not one transaction. Unsafe nonregular files, including FIFOs, MUST fail without blocking in open.
Do not unlink or replace the lock while the namespace is in use. This is a proposed localfs reader primitive;
no change to the shared core lock API is required. Preserve unsupported-platform and timeout errors.

An absent namespace returns an empty result only after an actual ENOENT observation; it creates nothing. That
observation may precede a concurrent first registration. An existing namespace without a lock is an initialization
or damage condition: fail with `SPEC_SCOPE_SHARED_PATH_UNAVAILABLE`, never read unlocked or silently initialize.
An authorized registration from a worktree without an owner token reaches existing lock initialization; queries
never do so. Release and sweep may query first and MUST NOT be advertised as missing-lock recovery. For a damaged
namespace without an eligible registration, require explicit operator repair of the missing lock after writers
are quiescent; do not remove records, tokens or replace an existing lock to recover. Permission,
unsafe-path and other IO failures are errors, not evidence of empty state. Existing per-record invalid-data warnings
remain visible, and no empty or partial registry result certifies that active work has no overlap.

Keep configured absolute `shared_path` and namespace behavior unchanged. This work adds no MCP server, implicit
fallback, relocation, sandbox settings, permission provisioner or new policy configuration. Mutations still need
access to the namespace (lock, record temporaries, records and journal) and, when applicable, the worktree Git
directory (token, token temporaries and cleanup). Hosts grant exact command-scoped access where needed; refusal
stops that operation. A successful read grants no mutation permission.

The affected contract is `CAP-COLL-work-scope-registry`. `CAP-DLV-project-policy` is examined but unchanged because
configuration and host authorization remain unchanged. Development targets the scope implementation, CLI tests
and collaboration contract; medium Development effort remains appropriate. Ordinary Git writes remain separate.

### Verification scenarios for the selected direction

- **V1:** From a base checkout and two linked worktrees, registered scope is mutually visible and overlaps are
  reported against the same registry; an unrelated repository remains isolated.
- **V2:** With `.git` read-only and explicitly enumerated writable roots, document which operations succeed, which
  require scoped approval and why. Include a linked worktree without access to the proposed shared directory.
- **V3:** For queries of absent and populated state, enumerate filesystem side effects and demonstrate the selected
  consistency behavior during concurrent updates; do not report a failed read as an empty registry.
- **V4:** Across concurrent registration, process interruption, session restart and worktree removal, verify token
  ownership, atomicity and recovery without unintended record loss or cross-worktree token reuse.
- **V5:** If MCP is selected, verify authorized calls, denied calls and server unavailability. If file relocation is
  selected, verify path discovery, ignore rules and per-worktree token placement together.

### Non-goals

- Implementing a general-purpose agent scratchpad, remote multi-host coordination or a new authentication platform.
- Disabling sandbox protections globally, guaranteeing approval from every host, or removing Git's own write needs.
- Selecting MCP or relocating state solely because a sandboxed command failed once.
- Changing production behavior or current capability contracts as part of this draft.

## 4. Lifecycle & Retirement Criteria

Planning recommends the bounded read-access change at feature/proposal depth, with medium Planning and Development
effort. Acceptance and implementation remain separate user-controlled transitions.

Planning is ready for acceptance when it provides an evidence-backed comparison, recommends a direction (including
retaining the baseline), identifies all storage and permission boundaries, answers the spike questions and maps the
verification scenarios to executable checks. Record the selected architectural decisions as proposal decisions;
review Development effort against the resulting scope before handoff.

If the baseline is retained without implementation, close the proposal with its rationale and operational guidance
rather than creating an empty Development unit. If a change is selected, obtain plan acceptance before handoff and
reconcile only the contracts affected by the implemented direction.
