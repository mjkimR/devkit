---
id: MAT-scope-activity-write-probe
title: Scope collection probe of parallel Planning and one Development unit
summary: "Record a read-only refs-mode scope collection over six Planning branches and one Development branch, showing where current writes, future impact and coverage gaps appear in today's output."
created_at: 2026-10-30
---

# [MAT-scope-activity-write-probe] Scope collection probe of parallel Planning and one Development unit

## Evidence boundary

- Repository: devkit, base `main` at `fdba6646`, probed from the `plan-scope-activity-write-evidence` worktree.
- Command: `uv run devkit spec scope collect --mode refs --format json` (exit 0). `refs` mode reads pinned trees
  and the registry with shared locking only, so no sibling worktree was opened.
- Sources: six `plan-*` branches of `MS-git-operator-lifecycle-refinement`, `dev-rename-incubation-to-adaptive-dev`
  and its creation snapshot. Result: 8 observations, 21 pairs, 0 overlapping, `coverage=partial` with 7 problems.

## Observations

| Source | Declared and candidate paths | Observed paths | Unresolved inputs | Gap reason |
| --- | --- | --- | --- | --- |
| Four Planning branches with one commit | none | `docs/proposals/PROP-<slug>/proposal.md` | `missing-target-docs` | `unresolved-input` |
| Two Planning branches at the base commit (`fdba6646`) | none | none | `missing-target-docs`, `unknown-base` | `unknown-base` |
| `dev-rename-incubation-to-adaptive-dev` | 22 `declared-code` paths | 170 committed doc and code paths, none under another proposal directory | 20 `excluded-tree` (`_Boundary` entries under `docs/` and `specs/`), `missing-reconcile` | `unresolved-input` |
| Its creation snapshot | none | proposal and decision paths at creation | `missing-tasks`, `missing-reconcile` | none (snapshot) |

## Findings

1. **Gap reasons hide their inputs.** The partial-coverage detail names a source and `unresolved-input` only. The
   Host must open the JSON `observations[].scope.unresolved` list to learn that a Planning gap is
   `missing-target-docs` and the Development gap is `missing-reconcile` plus `docs/` boundaries. This matches the
   Host's observation on 2026-10-30 of `unresolved-input` for the Development branch and worktree.
2. **A branch at its base commit reports `unknown-base`.** `Collector.observe` clears `base_sha` when it equals the
   candidate's commit, and `committed()` then records `unknown-base`. The committed range of such a branch is known
   to be empty; a freshly prepared Planning or Development worktree therefore shows a false gap at the moment the
   Host schedules parallel work.
3. **No overlap here, but nothing tells current from future.** In this repository no proposal has `target-docs.md`,
   so no candidates exist and the pairs are empty. In the consumer pilot (`MAT-git-operator-consumer-pilot`, row
   "Future-impact overlap") the proposals declared capability targets whose `entrypoints` overlapped as `candidate`
   paths, while each Planning run wrote only its proposal directory. The evidence line names `source=` and
   `other_source=`, but neither line nor pair says whether the overlap concerns the activities running now.
4. **The scheduling instruction reads any overlap.** `spec-orchestrate` runs "units overlapping in
   `devkit spec scope collect --mode worktrees`" sequentially. A future-impact candidate overlap between two
   Planning units therefore serializes Planning runs whose writes are disjoint, which is what the pilot Host had to
   explain away.
