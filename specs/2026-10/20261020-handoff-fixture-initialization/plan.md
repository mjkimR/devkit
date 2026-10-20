---
id: PLAN-handoff-fixture-initialization
spec: SPEC-handoff-fixture-initialization
---

# Technical Plan: `SPEC-handoff-fixture-initialization`

## 1. Constitution & Invariant Review

No architecture or production contract changes. Tests stay in the existing package test directory. Production
handoff calls, subprocesses and test selection remain real and unchanged. No ADR or dependency is required.

## 2. Impacted Components and Design

- Add a typed module-scoped synchronized repository fixture in `packages/devkit-spec/tests/test_integration.py`.
  Build it through `_make_synced_repo`, `_cli(..., "sync")` and the existing preparation commit.
- Keep `accepted_handoff_base` function-scoped. Copy the standalone seed with independent files and preserved
  symlinks, then perform the existing worktree, proposal, refinement and merge steps without modification.
- Stop reuse before worktree creation. The diagnostic completed-state copy omitted `.git/worktrees`; this design
  never needs deletion, repair or rewriting of Git worktree metadata and preserves the original topology.
- Add a regression that mutates a case's refs, config, tracked content and ignored assets and verifies seed isolation.
- Retain a dated measurement driver and report under `docs/materials/2026-10/20261020-handoff-fixture-initialization/`.
  Load the baseline test file from the entry commit into temporary storage; select the same twelve original cases,
  use the current interpreter/configuration, and record serial and reversed-order parallel samples.

## 3. Failure Modes

Independent copies prevent mutable Git state leakage. Create the seed before linked worktrees exist, so copied
Git paths stay local. Existing full-file handoff assertions cover native registration paths and runtime checks.
The seed itself executes real sync and commits in each worker. A smaller reuse boundary may save less time than
the diagnostic prototype; report actual measurements and retain correctness rather than widening the cache.

## 4. Verification

- Run the integration file serially and with default eight-worker worksteal execution.
- Run `just lint-check spec`, `just check spec` and `just test-affected --base main`, retaining full fallback.
- Check governance and spec task coverage, and run the reproducible paired measurement driver.
- Obtain the mandatory medium independent code review; reconcile the test-only no-impact result explicitly.
