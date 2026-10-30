---
id: PROP-scope-activity-write-evidence
title: Show current activity writes beside future implementation impact in scope output
summary: "Show each current activity's actual write boundaries in scope inspection separately from declared or candidate future implementation impact, keeping every overlap and coverage gap visible and the output informational."
status: reviewing
created_at: 2026-10-30
target_area: capabilities/collaboration/
priority: medium
size: M
planning_effort: medium
dev_effort: medium
milestone: MS-git-operator-lifecycle-refinement
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/features/scope/
    - packages/devkit-spec/tests/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/
    - docs/capabilities/collaboration/
    - docs/capabilities/harness/CAP-HARN-agent-guidance.md
    - docs/usecases/collaboration/UC-run-parallel-work-safely.md
  excludes:
    - .devkit/managed/
    - packages/devkit-core/
task_kind: feature
decomposed_from: PROP-git-operator-pilot-follow-up
workflow: sdd-proposal
---

# [PROP-scope-activity-write-evidence] Show current activity writes beside future implementation impact in scope output

## 1. Background & Hypothesis

In the resource-indexer consumer pilot (`MAT-git-operator-consumer-pilot`), scope observations exposed future
implementation candidates while current Planning writers owned distinct proposal directories. The Host had to explain
that difference before parallel Planning could proceed.

The hypothesis: scope output that shows each current activity's actual write boundaries (a Planning run writes only
its proposal directory) beside declared or candidate future impact lets the Host schedule without re-deriving it.
`CAP-COLL-work-scope-registry` owns this informational evidence.

## 2. Technical Spike Questions

- **Q1 Presentation**: Can scope output show current activity write boundaries beside declared and candidate
  implementation impact without hiding unresolved inputs, suppressing overlaps or becoming write authority?
- **Q2 Provenance**: How do candidate and observed provenance and the partial-coverage signal stay visible?

## 3. Proposed Design & Impact

Evidence: `MAT-scope-activity-write-probe` (this proposal's `materials/`) and `MAT-git-operator-consumer-pilot`
(row "Future-impact overlap").

### 3.1 Horizon of each path and overlap

Every path of an observation gets a `horizon`, derived from the unit kind `collect` already identifies; no input or
path is added.

| Path | Planning activity (proposal unit) | Development activity (spec unit, or a snapshot record) |
| --- | --- | --- |
| `observed` (committed, staged, unstaged, untracked) | `current` | `current` |
| `declared-doc`, `declared-code`, `candidate` | `future` | `current` |

An observation without a task identity (`identity-ambiguous` dirty paths) has only observed paths, so they are
`current`. An evidence entry is `current` when both of its sides are `current`, otherwise `future`.

- JSON: each evidence entry gains `horizon`; each pair gains `current` and `future` entry counts; `summary` gains
  `current_overlapping` (pairs with at least one `current` entry).
- Text: `[EVIDENCE: ... horizon=current|future]`, `[PAIR: ... current=<n> future=<n>]` and
  `[SUMMARY: ... current_overlapping=<n>]`.
- `docs=`, `code=`, `unresolved=`, `overlapping=` and the overlap definition (`CAP-COLL-work-scope-registry` 4.2) do
  not change: every overlap stays listed and counted.

### 3.2 Coverage gaps name their inputs

- A source's `unresolved-input` problem carries the distinct reasons of its unresolved inputs: JSON
  `coverage.problems[].inputs`, and the `SPEC_SCOPE_COLLECTION_PARTIAL` detail
  `refs/heads/dev-x: unresolved-input (excluded-tree, missing-reconcile)`.
- Every reason still counts as a gap; lifecycle-normal ones (`missing-target-docs`, `missing-reconcile`) are not
  reclassified as covered.
- A branch whose commit equals its selected base, and whose ref is not the base ref itself, has an empty committed
  range: `committed` is an observed layer with no paths, not `unknown-base` (finding 2 of
  `MAT-scope-activity-write-probe`).

### 3.3 Host scheduling text

- `spec-orchestrate`: units whose `current` evidence overlaps run sequentially. A pair with only `future` evidence
  does not serialize their Planning runs; it informs handoff and integration order. Partial coverage stays an input
  to both choices, never a proof of independence.
- `CAP-HARN-agent-guidance` (Host scope observation) and `UC-run-parallel-work-safely` (step 6 and a GOP-04
  scenario) state the same reading. `CAP-COLL-work-scope-registry` 4.5 and 4.9 carry the output contract.
- The Host keeps the scheduling decision; no result grants or refuses a write.

Acceptance check (from the parent's verification candidates):

| ID | Given | When | Then |
| --- | --- | --- | --- |
| GOP-04 | Disjoint proposal-only Planning writes and overlapping future implementation candidates | Scope is inspected for scheduling | Both facts and unresolved coverage remain visible; the result grants or refuses no write and the Host retains the decision. |
| SAW-01 | Two Planning units whose targets' `entrypoints` overlap and whose observed paths are their own proposal directories | `devkit spec scope collect` runs | The pair lists the candidate overlap with `horizon=future`, `current=0`, unchanged `code=`, and `current_overlapping` excludes it. |
| SAW-02 | A Planning unit's candidate overlaps a Development unit's declared or observed code | Scope is collected | The entry is `future`; the Development unit's own paths stay `current`. |
| SAW-03 | A Development unit with `_Boundary` entries under `docs/` and no `reconcile.md` | Scope is collected | The partial-coverage detail and `coverage.problems[].inputs` name `excluded-tree` and `missing-reconcile`; coverage stays `partial`. |
| SAW-04 | A `plan-*` branch at the same commit as its base | Scope is collected | `committed` is observed with no paths and the source reports no `unknown-base`. |

### Non-goals

- **Scope Excluded**: claiming that informational scope observations authorize writes, or that unresolved coverage
  means no conflict.
- **Scope Excluded**: redefining overlap to hide it, or dropping a `future` overlap from counts or output.
- **Scope Excluded**: synthesizing a role's write boundary (such as a Planning worker's proposal directory) as a path;
  current writes come from observed and declared evidence only.
- **Scope Excluded**: treating `_Boundary` entries under `docs/` as document declarations (`CAP-TRACE-code-entrypoints`
  keeps them `excluded-tree`).

## Planning decisions

- Settled in this Planning run, pending the user's answers recorded in the `worker` envelope: horizon tags over
  separate lists (3.1), naming gap inputs and the empty-range fix (3.2).

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-scope-activity-write-evidence`; the proposal is deleted there and its decisions become ADRs.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
