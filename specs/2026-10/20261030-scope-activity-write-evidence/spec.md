---
id: SPEC-scope-activity-write-evidence
title: Show current activity writes beside future implementation impact in scope output
summary: Show each current activity's actual write boundaries in scope inspection separately from declared or candidate future implementation impact, keeping every overlap and coverage gap visible and the output informational.
status: planned
created: 2026-10-30
decomposed_from: PROP-git-operator-pilot-follow-up
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-scope-activity-write-evidence] Show current activity writes beside future implementation impact in scope output

## 1. Problem Statement & Motivation

Handed off from proposal PROP-scope-activity-write-evidence on 2026-10-30.
- **Preserved Materials**: `docs/materials/2026-10/20261030-scope-activity-write-evidence`

### 1. Background & Hypothesis

In the resource-indexer consumer pilot (`MAT-git-operator-consumer-pilot`), scope observations exposed future
implementation candidates while current Planning writers owned distinct proposal directories. The Host had to explain
that difference before parallel Planning could proceed.

The hypothesis: scope output that shows each current activity's actual write boundaries (a Planning run writes only
its proposal directory) beside declared or candidate future impact lets the Host schedule without re-deriving it.
`CAP-COLL-work-scope-registry` owns this informational evidence.

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Show current activity writes beside future implementation impact in scope output so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Technical Spike Questions

- **Q1 Presentation**: Can scope output show current activity write boundaries beside declared and candidate
  implementation impact without hiding unresolved inputs, suppressing overlaps or becoming write authority?
- **Q2 Provenance**: How do candidate and observed provenance and the partial-coverage signal stay visible?

### 3. Proposed Design & Impact

Evidence: `MAT-scope-activity-write-probe` (this proposal's `materials/`) and `MAT-git-operator-consumer-pilot`
(row "Future-impact overlap").

#### 3.1 Horizon of each path and overlap

Every path of an observation gets a `horizon`, derived from the activity `collect` already identifies; no input or
path is added.

| Path | Planning activity | Any other observation |
| --- | --- | --- |
| `observed` (committed, staged, unstaged, untracked) | `current` | `current` |
| `declared-doc`, `declared-code`, `candidate` | `future` | `current` |

- A Planning activity is an observation whose `provenance.unit` is a proposal unit and whose source is a `plan-*`
  ref or worktree. A proposal unit observed on a `dev-*` ref or worktree (a handoff before its first commit), a spec
  unit, a snapshot record and an observation without a unit (`identity-ambiguous` dirty paths) are all `current`.
- The unit kind comes from `provenance.unit`, never from `task_key`, which snapshots and duplicate anchors leave
  empty.
- An evidence entry is `current` when both of its sides are `current`, otherwise `future`.
- JSON: each evidence entry gains `horizon`; each pair gains `current` and `future` entry counts
  (`current + future = len(docs) + len(code)`); `summary` gains `current_overlapping` (pairs with at least one
  `current` entry).
- Text: `[EVIDENCE: ... horizon=current|future]`, `[PAIR: ... current=<n> future=<n>]` and
  `[SUMMARY: ... current_overlapping=<n>]`.
- `docs=`, `code=`, `unresolved=`, `overlapping=` and the overlap definition (`CAP-COLL-work-scope-registry` 4.2) do
  not change: every overlap stays listed and counted.

#### 3.2 Coverage gaps name their inputs

- A source's coverage problem carries the distinct reasons of its unresolved inputs, whatever the problem's own
  reason (`unresolved-input` or `unknown-base`): JSON `coverage.problems[].inputs`, and the
  `SPEC_SCOPE_COLLECTION_PARTIAL` detail `refs/heads/dev-x: unresolved-input (excluded-tree, missing-reconcile)`.
- Every reason still counts as a gap; lifecycle-normal ones (`missing-target-docs`, `missing-reconcile`) are not
  reclassified as covered.
- A selected base whose commit equals the branch tip is still a base: `collect` stops clearing it, and `committed()`
  computes the range by `CAP-COLL-work-scope-registry` 4.1 (empty without a registration cap). A base is discarded,
  and stays `unknown-base`, only when it resolves (`git rev-parse --symbolic-full-name`) to the candidate's own full
  ref or to a tracking peer of the same task. This removes the false gap of a freshly prepared branch (finding 2 of
  `MAT-scope-activity-write-probe`).

#### 3.3 Host scheduling text

- `spec-orchestrate`: units whose `current` evidence overlaps run sequentially. A pair with only `future` evidence
  does not serialize their Planning runs.
- Before handing a unit off, the Host treats its `future` evidence as `current`: units whose `future` evidence
  overlaps are handed off or integrated sequentially.
- Partial coverage stays an input to both choices, never a proof of independence.
- `CAP-HARN-agent-guidance` (Host scope observation) and `UC-run-parallel-work-safely` (step 6 and a GOP-04
  scenario) state the same reading. `CAP-COLL-work-scope-registry` 4.5 and 4.9 carry the output contract.
- The Host keeps the scheduling decision; no result grants or refuses a write.

Acceptance check (from the parent's verification candidates):

| ID | Given | When | Then |
| --- | --- | --- | --- |
| GOP-04 | Disjoint proposal-only Planning writes and overlapping future implementation candidates | Scope is inspected for scheduling | Exit is 0 without `--strict`; the observed proposal paths, the `future` evidence and the unresolved inputs are all in the output; no field grants or refuses a write. |
| SAW-01 | Two `plan-*` units whose targets' `entrypoints` overlap and whose observed paths are their own proposal directories | `devkit spec scope collect` runs | Each candidate entry has `horizon=future`; the pair has `current=0`, `code=` equal to its code evidence entries and `current+future = docs+code`; `current_overlapping` excludes the pair and `overlapping` includes it. |
| SAW-02 | A `plan-*` unit's candidate overlaps a Development unit's declared or observed code | Scope is collected | The entry is `future`; the Development unit's own paths stay `current`. |
| SAW-03 | A `dev-*` ref at its base commit whose pinned tree holds only the accepted proposal | Scope is collected | Its declared and candidate paths are `current`. |
| SAW-04 | A Development unit with `_Boundary` entries under `docs/` and no `reconcile.md` | Scope is collected | The partial-coverage detail and `coverage.problems[].inputs` name `excluded-tree` and `missing-reconcile`; coverage stays `partial`. |
| SAW-05 | A `plan-*` branch at the same commit as its base, the proposal file present at that commit | Scope is collected | The source is observed, its layers include `committed` with no committed paths, and no `unknown-base` problem names it. |
| SAW-06 | `--base` or `branch.<b>.devkitBase` names the branch itself (short name or `HEAD`) | Scope is collected | The source reports `unknown-base`, never an empty range. |

#### Non-goals

- **Scope Excluded**: claiming that informational scope observations authorize writes, or that unresolved coverage
  means no conflict.
- **Scope Excluded**: redefining overlap to hide it, or dropping a `future` overlap from counts or output.
- **Scope Excluded**: synthesizing a role's write boundary (such as a Planning worker's proposal directory) as a path;
  current writes come from observed and declared evidence only.
- **Scope Excluded**: treating `_Boundary` entries under `docs/` as document declarations (`CAP-TRACE-code-entrypoints`
  keeps them `excluded-tree`).

### Planning decisions

- The user chose horizon output in `collect` and the scheduling text (3.1, 3.3) over a skill-only reading of the
  existing `unit=` and `source=` fields, because the Host would otherwise join every evidence line to its observation.
- The user included both coverage-gap fixes (3.2): every source problem names its unresolved input reasons, and the
  self-base guard removes the false `unknown-base` of a branch at its base commit.
- The other children of `MS-git-operator-lifecycle-refinement` also own `spec-orchestrate/`, and Development
  integrates them one at a time. This unit changes only the scope-reading text there and keeps a sibling's text that
  reached the base first.
- Folded from `challenger-01`: the Planning horizon applies only on `plan-*` sources (3.1); future-only overlap
  serializes handoff and integration (3.3); the self-base guard compares resolved refs (3.2); gap inputs travel with
  every problem reason (3.2); the acceptance checks state mechanical assertions.

### 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-scope-activity-write-evidence`; the proposal is deleted there and its decisions become ADRs.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.

