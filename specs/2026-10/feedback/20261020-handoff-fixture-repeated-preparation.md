---
id: FB-handoff-fixture-repeated-preparation
title: Reuse isolated prepared repositories in handoff tests
scope: repo
kind: suggestion
category: redundant-step
target: packages/devkit-spec/tests/test_integration.py::accepted_handoff_base
skill: spec-feedback
agent: codex
origin: agent
severity: noise
recurring: true
status: resolved
created_at: 2026-10-20
---

# [FB-handoff-fixture-repeated-preparation] Reuse isolated prepared repositories in handoff tests

## Suggestion

- **Current Procedure**: Each of twelve handoff cases builds an independent repository, synchronizes assets,
  commits projections, creates a Planning worktree, completes a proposal, refines it and merges it to the base.
  The module-scoped `synced_template` already reuses an initial asset sync, but the function-scoped
  `accepted_handoff_base` repeats the remaining preparation.
- **Proposed Procedure**: Evaluate a worker-local prepared repository seed, created through the real preparation
  functions, and independently copy it for each test. Keep tested handoff, approval, stale-base and registration
  operations real. Begin with a seed before linked-worktree creation if preserving the original worktree topology
  would otherwise require complex repair.
- **Expected Benefit**: Avoid repeated sync and preparation commits. A completed-state prototype reduced the
  twelve-case serial execution from 62.24 to 23.58 seconds; two eight-worker comparisons saved 2.22–3.83 seconds.
  These are local measurements, not a promised workspace-wide speedup.
- **Cost & Risk**: Repositories cannot share mutable refs, indexes or working files. Registered linked worktrees
  contain absolute paths; copying their metadata can retain references to the seed. The prototype omitted
  `.git/worktrees`, which changes the initial topology and needs explicit coverage review before adoption.
  Check local config, hooks, ignored assets, transient registries and registration files for seed paths. Worker
  isolation limits reuse: the twelve-case parallel runs built eight seeds, rather than one shared seed.
- **Attempted**: Temporary pytest plugins instrumented existing functions and replaced only the fixture during
  diagnostic runs. The prototype copied Git objects and refs as independent files, preserved symlinks, omitted
  linked-worktree registrations, checked each copy was clean and listed only itself, and checked the seed refs and
  working tree were unchanged afterward. All twelve cases passed in each of six executions. Repository test
  sources were not changed; no optimization is implemented.

## Diagnostic Details

- **Reproduction**: Select the twelve cases whose fixture closure contains `accepted_handoff_base`. Time fixture
  setup and `_make_synced_repo`, `_cli`, `_start_worktree`, `_complete_proposal` and `git` with temporary wrappers.
  Compare the original fixture with a worker-local seed built by the original fixture and independently copied
  into each test's temporary directory. Run both with `-n0`, then `-n auto --maxprocesses 8 --dist worksteal` twice
  with reversed order. Disable pytest's cache provider; retain existing assertions and test bodies.
- **Expected / Actual**: No latency contract exists. Serial original fixture setup totaled 39.94 seconds across
  twelve cases, including 22.02 seconds in repeated `_cli(repo, "sync")` and 6.16 seconds inside proposal
  completion. Prototype setup totaled 4.78 seconds including seed creation, with a median copy-and-check time
  of 0.17 seconds. Nested timings overlap and must not be added.
- **Versions**: Source revision `6b21869d9029e22886fc6d5511b82c67bc9297cc`; Python 3.12.3.
- **Conditions**: Existing workspace interpreter and warm local filesystem; permitted local sockets and real
  subprocesses. Only the twelve fixture consumers were executed, not the entire integration file or workspace.
  Parallel elapsed times include pytest process startup; serial figures are pytest-reported elapsed times.
- **Workarounds Attempted**: Initial asset sync is already module-scoped and `_cli` already uses in-process
  `CliRunner`. The completed-state prototype demonstrates feasibility, not equivalent coverage of every possible
  repository topology or a production-ready shared fixture.
- **Related Assets**: `packages/devkit-spec/tests/test_integration.py`, its `synced_template`,
  `accepted_handoff_base`, `_make_synced_repo` and `_complete_proposal` helpers, and
  `packages/devkit-spec/src/devkit_spec/handoff_mcp.py`.

## Evidence

```text
Serial, existing test bodies: original 62.24 s; prototype 23.58 s; 12 passed in each.
Parallel pair 1, original then prototype: 19.336 s -> 15.505 s; 12 passed in each.
Parallel pair 2, prototype then original: original 19.451 s; prototype 17.234 s; 12 passed in each.
Original accepted_handoff_base: 12 calls, 39.938 s total, 3.436 s median.
Prototype accepted_handoff_base: 12 calls, 4.782 s total, including one seed build.
Prototype independent copy and checks: 12 calls, 1.925 s total, 0.166 s median.
Parallel prototype: eight independent worker seeds; twelve independent test copies.
Seed refs and working tree unchanged after every prototype execution.
```

## Disposition

Resolved by `SPEC-handoff-fixture-initialization`: a worker-local synchronized standalone repository template
replaces repeated sync and preparation commits. Each independent case copy still creates its real Planning
worktree and accepted proposal, preserving the original topology without removing or repairing Git metadata.
Independent medium code review passed without findings. Affected verification passed 30 tests, including all
21 integration cases and the new Git/config/tracked-file/ignored-asset isolation regression; lint, format,
Pyright and cumulative governance passed. The same twelve original cases passed all six measurement runs:
serial elapsed time fell from 46.168 to 29.222 seconds; eight-worker medians fell from 16.988 to 14.803 seconds
(12.9 percent). Preparation sync calls fell from twelve to one serially and twelve to eight in parallel.
Reproduction and source hashes are retained in `docs/materials/2026-10/20261020-handoff-fixture-initialization/`.
These are local measurements, not a portable latency guarantee. Resolution on the task branch does not assert
integration into the base branch.
