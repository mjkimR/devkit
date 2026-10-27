---
id: PADR-classify-performance-changes-by-observable-behavior
title: Classify performance changes by observable behavior
summary: For performance changes, we count only changes that keep every observable result, error path and persisted format as behavior-preserving and route new cross-run state, concurrency or output changes as contract changes, accepting more separate work items.
proposal: PROP-performance-pass
status: draft
created_at: 2026-10-27
---

# [PADR-classify-performance-changes-by-observable-behavior] Classify performance changes by observable behavior

- **Status**: Draft
- **Date**: 2026-10-27

---

## 1. Context & Problem Statement

Faster code often changes behavior on inputs the corpus does not contain: a scan API that raises where the old call
returned `False` broke every listing on one symlink loop (`materials/pass-evidence.md` §2). Some speedups change the
contract outright: state kept between runs can serve stale answers and occupies disk; concurrency changes ordering,
error reporting and resource use. `review-refactor` routes behavior-preserving changes as refactors and contract
changes as their own work items; performance changes need the same split with criteria of their own.

## 2. Decision Drivers

- A change routed as a refactor changes no observable behavior for any accepted input.
- Internal caches and memos stay usable when their invalidation is proved.
- The split matches `review-refactor`'s dispositions so application is shared.

## 3. Considered Options

- **Observable-behavior criteria with named contract-change classes** (selected): clear routing; more work items.
- **Corpus-equivalence only**: cheap; misses error paths, as the regression showed.
- **Every performance change as a contract change**: safest; turns internal speedups into full feature work.

## 4. Decision Outcome

- Behavior-preserving: stdout, stderr, exit codes, written files and their bytes, persisted formats other versions or
  tools read, error behavior (which inputs fail and how) and the order of observable side effects stay the same for
  every accepted input.
  - A change to a private cache's format qualifies when a version or fingerprint invalidates old entries and outputs
    are identical with the cache off, cold and warm.
  - A memo within one run qualifies when its key covers every input that changes the answer and failures are never
    memoized.
- Contract change: changed output (content, order or format); new state that persists between runs where none
  existed (a cache file, a daemon); concurrency or parallelism that can change ordering, errors, locking or resource
  use; changed defaults, accuracy or error handling; a removed option. It is its own work item through the
  repository's normal development workflow, as in `review-refactor`.
- Differential comparison runs old and new on the repository's corpus plus the input domain's edge and error cases
  (empty, malformed, unreadable, symbolic link loops, differently spelled paths, a vanished working directory).
- Any difference the comparison or the review finds is fixed, or the change returns to the decision round as its own
  contract-change work item; unlike `review-refactor`, no approved behavior change stays in the behavior-preserving
  work item.

## 5. Consequences

- Positive: a speedup that changes a contract is visible in the decision round and gets its own review.
- Negative: caching or concurrency proposals need a separate work item even when small.
- Follow-up: none.

## 6. Confirmation

Review only (the playbook's `references/candidates.md` states the criteria; each change record names its
classification and differential inputs).
