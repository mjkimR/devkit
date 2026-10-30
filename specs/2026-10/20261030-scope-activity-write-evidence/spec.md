---
id: SPEC-scope-activity-write-evidence
title: Show current activity writes beside future implementation impact in scope output
summary: Show each current activity's actual write boundaries in scope inspection separately from declared or candidate future implementation impact, keeping every overlap and coverage gap visible and the output informational.
status: completed
created: 2026-10-30
decomposed_from: PROP-git-operator-pilot-follow-up
related_capabilities: [CAP-COLL-work-scope-registry, CAP-HARN-agent-guidance]
related_usecases: [UC-run-parallel-work-safely]
workflow: sdd-spec-feature
---

# [SPEC-scope-activity-write-evidence] Show current activity writes beside future implementation impact in scope output

## 1. Problem Statement & Motivation

Handed off from proposal PROP-scope-activity-write-evidence on 2026-10-30.
- **Preserved Materials**: `docs/materials/2026-10/20261030-scope-activity-write-evidence`

### 1.1 Background & Hypothesis

In the resource-indexer consumer pilot (`MAT-git-operator-consumer-pilot`), scope observations exposed future
implementation candidates while current Planning writers owned distinct proposal directories. The Host had to explain
that difference before parallel Planning could proceed.

The hypothesis: scope output that shows each current activity's actual write boundaries (a Planning run writes only
its proposal directory) beside declared or candidate future impact lets the Host schedule without re-deriving it.
`CAP-COLL-work-scope-registry` owns this informational evidence.

### 1.2 Evidence

`MAT-scope-activity-write-probe` (preserved materials) records a read-only `refs` collection over six Planning
branches and one Development branch, and `MAT-git-operator-consumer-pilot` (row "Future-impact overlap") the pilot.
Their findings, checked against the current base (`Collector.observe`, `committed()`, `collection_output.render`
and `spec-orchestrate`), still hold:

1. The `SPEC_SCOPE_COLLECTION_PARTIAL` detail names a source and `unresolved-input` only; its inputs
   (`missing-target-docs`, `missing-reconcile`, `excluded-tree`) live only in `observations[].scope.unresolved`.
2. `Collector.observe` clears a selected base whose commit equals the candidate's tip, so `committed()` records
   `unknown-base` for a freshly prepared branch whose committed range is known to be empty.
3. No evidence line, pair or summary tells an overlap of the activities running now from one of future
   implementation impact.
4. `spec-orchestrate` serializes any overlap in `devkit spec scope collect`, so a candidate overlap between two
   Planning units serializes Planning runs whose writes are disjoint.

`UC-run-parallel-work-safely` (step 6) is the use case whose reading changes.

## 2. User Stories

- **US-1**: As the orchestrating Host, I want each overlap labelled with whether it concerns the activities running
  now or future implementation impact, so that I can run disjoint Planning turns in parallel while still ordering
  handoff and integration by future impact.
- **US-2**: As the orchestrating Host, I want each coverage gap to name the unresolved inputs behind it and no false
  gap for a branch at its base commit, so that I can tell lifecycle-normal gaps from missing evidence without opening
  the JSON observations.

## 3. Non-Goals

1. **Scope Excluded**: claiming that informational scope observations authorize writes, or that unresolved coverage
   means no conflict.
2. **Scope Excluded**: redefining overlap to hide it, or dropping a `future` overlap from counts or output; `docs=`,
   `code=`, `unresolved=`, `overlapping=` and the overlap definition (`CAP-COLL-work-scope-registry` 4.2) do not
   change.
3. **Scope Excluded**: synthesizing a role's write boundary (such as a Planning worker's proposal directory) as a
   path; current writes come from observed and declared evidence only.
4. **Scope Excluded**: treating `_Boundary` entries under `docs/` as document declarations
   (`CAP-TRACE-code-entrypoints` keeps them `excluded-tree`), or reclassifying a lifecycle-normal gap
   (`missing-target-docs`, `missing-reconcile`) as covered.
5. **Scope Excluded**: horizon output for `compare`, `query` and `update`, whose sources carry no activity; they keep
   their output unchanged.

## 4. Acceptance Criteria & Behavioral Contracts

The contract the scenarios below verify:

**Horizon.** Every path of a `collect` observation has a horizon derived from the activity `collect` already
identifies; no input or path is added.

| Path source | Planning activity | Any other observation |
| --- | --- | --- |
| `observed` (committed, staged, unstaged, untracked) | `current` | `current` |
| `declared-doc`, `declared-code`, `candidate` | `future` | `current` |

- A Planning activity is an observation whose `provenance.unit` is a proposal unit (`docs/proposals/PROP-<slug>`)
  and whose source is a `plan-*` ref or worktree (the last segment of `provenance.ref`). A proposal unit observed on
  a `dev-*` ref or worktree (a handoff before its first commit), a spec unit, a snapshot record and an observation
  without a unit (`identity-ambiguous` dirty paths) are `current`. The unit kind comes from `provenance.unit`, never
  from `task_key`.
- An evidence entry is `current` when both of its sides are `current`, otherwise `future`.
- JSON: each evidence entry gains `horizon`; each pair gains `current` and `future` entry counts
  (`current + future = len(docs) + len(code)`); `summary` gains `current_overlapping` (pairs with at least one
  `current` entry).
- Text: `[EVIDENCE: ... horizon=current|future]`, `[PAIR: ... current=<n> future=<n>]` and
  `[SUMMARY: ... overlapping=<n> current_overlapping=<n> ...]`.

**Coverage gaps name their inputs.** Each `coverage.problems[]` entry has `inputs`, the sorted distinct reasons of
the source's unresolved inputs, whatever the problem's own reason (`unresolved-input` or `unknown-base`); an entry
from no unresolved input has `inputs: []`. A `SPEC_SCOPE_COLLECTION_PARTIAL` detail with inputs reads
`<source>: <reason> (<input>, <input>)`. Every reason still counts as a gap.

**Self-base guard.** A selected base whose commit equals the branch tip is still a base: `collect` keeps it, and the
committed range follows `CAP-COLL-work-scope-registry` 4.1 (empty without a registration cap). The base is discarded,
and the source stays `unknown-base`, only when `git rev-parse --symbolic-full-name <base>` resolves to the
candidate's own full ref or to a tracking peer of the same task (`refs/heads/<branch>` or
`refs/remotes/<remote>/<branch>` with the candidate's branch name).

**Scheduling.** Units whose `current` evidence overlaps run sequentially; a pair with only `future` evidence does
not serialize their Planning runs. Before handing a unit off, the Host treats its `future` evidence as `current`:
units whose `future` evidence overlaps are handed off or integrated sequentially. Partial coverage stays an input to
both choices, never a proof of independence. The Host keeps the decision; no result grants or refuses a write.

### [AC-01] Disjoint Planning writes with future overlap stay informational (GOP-04)
- **Given** two `plan-*` units whose committed paths are only their own proposal directories, whose targets'
  `entrypoints` overlap, and one of which declares a planned document target
- **When** the Host runs `devkit spec scope collect --mode refs --base main` in text and in JSON
- **Then** the exit code is 0 without `--strict` and 1 with it; the output lists each observed proposal path, a
  `horizon=future` evidence line and the `planned-doc` input in the partial-coverage detail; the JSON top-level keys
  are exactly `mode`, `started_at`, `finished_at`, `coverage`, `inventory`, `observations`, `pairs`, `summary` and
  `notices`, and each pair's keys are exactly `a`, `b`, `docs`, `code`, `unresolved`, `current` and `future`, so no
  field grants or refuses a write

### [AC-02] Planning candidate overlap is future (SAW-01)
- **Given** two `plan-*` units whose targets' `entrypoints` overlap and whose observed paths are their own proposal
  directories
- **When** `devkit spec scope collect` runs
- **Then** each evidence entry of their pair has `horizon=future`; the pair has `current=0`, `code=` equal to its
  code evidence entries and `current + future = docs + code`; `summary.current_overlapping` excludes the pair and
  `summary.overlapping` includes it

### [AC-03] Development paths stay current beside a Planning candidate (SAW-02)
- **Given** a `plan-*` unit whose candidate overlaps a Development unit's declared code, and a second Development unit
  declaring the same code
- **When** scope is collected
- **Then** the Planning/Development entry is `future`; the Development/Development entry is `current`; and a
  Planning `observed` path that overlaps the Development unit's declared code is a `current` entry

### [AC-04] A handed-off proposal on a dev-* ref is current (SAW-03)
- **Given** a `dev-*` ref at its base commit whose pinned tree holds only the accepted proposal with a target whose
  `entrypoints` overlap another unit's declared code
- **When** scope is collected
- **Then** its declared and candidate paths are `current`, so the overlap entry is `current`

### [AC-05] Coverage gaps name their unresolved inputs (SAW-04)
- **Given** a Development unit with `_Boundary` entries under `docs/` and no `reconcile.md`
- **When** scope is collected
- **Then** the partial-coverage detail reads `<source>: unresolved-input (excluded-tree, missing-reconcile)` (with any
  further input reasons in sorted order), `coverage.problems[].inputs` names `excluded-tree` and `missing-reconcile`,
  and `coverage.status` stays `partial`

### [AC-06] A branch at its base commit has a known empty range (SAW-05)
- **Given** a `plan-*` branch at the same commit as its base, the proposal file present at that commit
- **When** scope is collected with that base
- **Then** the source is observed, `observed_layers` includes `committed`, its scope has no observed path and no
  `unknown-base` problem or unresolved input names it

### [AC-07] A base naming the branch itself stays unknown (SAW-06)
- **Given** `--base` or `branch.<b>.devkitBase` naming the branch itself (its short name or `HEAD` in its checkout),
  or its tracking peer
- **When** scope is collected
- **Then** the source reports an `unknown-base` coverage problem and `committed` in `missing_layers`, never an empty
  range

### [AC-08] Host guidance reads current and future evidence
- **Given** the `spec-orchestrate` skill source, `CAP-HARN-agent-guidance` (Host scope observation),
  `UC-run-parallel-work-safely` and `CAP-COLL-work-scope-registry` 4.5 and 4.9
- **When** they are read after this change
- **Then** each states that `current` overlap serializes runs, that `future`-only overlap does not serialize Planning
  runs but orders handoff and integration, that partial coverage is never independence and that no result grants or
  refuses a write; the capability states the horizon, `inputs` and self-base contracts above

## 5. Assumptions

- `inputs` is present on every problem entry (empty for gaps that come from no unresolved input) so the JSON shape
  is stable; reasons are sorted for deterministic output. The proposal named the field without fixing these details.
- A problem repeated for one source and reason merges its inputs into the first entry; the problem count is unchanged.
- Code evidence keeps one entry per path pair. When a Planning side holds the same path as a candidate and as an
  observed write, the entry takes the `current` source, so a current overlap is never hidden behind a future one;
  `code=` counts are unchanged.
- A tracking peer is a ref with the candidate's inventoried branch name (the whole name under `refs/heads/` for a
  worktree, the last segment of a slash-free `plan-*`/`dev-*` ref) under `refs/heads/` or `refs/remotes/<remote>/` of
  a configured remote; the
  `plan-`/`dev-` prefix is part of the name, so `plan-x` and `dev-x` are not peers.
- A base that `git rev-parse --symbolic-full-name` cannot resolve to a ref (a commit ID, an ambiguous name) is kept
  as a commit, never discarded.
- `HEAD` as `--base` resolves in the checkout `collect` reads the source from: the collecting checkout for a ref
  source, the worktree for a worktree source.
- New text fields follow the existing ones: `horizon=` after `granularity=`, `current=`/`future=` after
  `unresolved=`, `current_overlapping=` after `overlapping=`.

## 6. Baseline

The before measurement is `MAT-scope-activity-write-probe` plus a run of this branch's head before the change on a
synthetic repository (two `plan-*` units with overlapping candidates, one `plan-*` branch at its base commit, one
`dev-*` unit with a `docs/` boundary and no `reconcile.md`): `overlapping=3`, details
`refs/heads/dev-d: unresolved-input` and `refs/heads/plan-c: unknown-base`, no horizon. The after measurement repeats
the same fixture on the changed head.
