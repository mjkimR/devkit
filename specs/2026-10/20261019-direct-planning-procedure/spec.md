---
id: SPEC-direct-planning-procedure
title: Planning procedure reachable from the spec skill for any executor
summary: Moves the ordered Planning steps out of the planning-worker contract into a spec skill reference that direct-mode Hosts and workers both follow, so the procedure lives in one place.
status: in-progress
created: 2026-10-19
related_capabilities:
  - CAP-DLV-delivery-workflows
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-direct-planning-procedure] Planning procedure reachable from the spec skill for any executor

## 1. Problem Statement & Motivation

Handed off from proposal PROP-direct-planning-procedure on 2026-10-19.

The `spec` skill's routing table says Planning "runs on `plan-<slug>` to `plan-accept`", and `effort.md` gives the
review depth per effort, but the ordered Planning steps (set `status: reviewing` and commit, record decisions as
PADRs, gather questions in one round, update `dev_effort`, sweep feedback, end with one `worker` envelope) are written
only in the `planning-worker` role contract. A Host running Planning in `direct` mode has to read a subagent contract
written for another actor (`FB-direct-planning-procedure-location`).

One Planning reference in the `spec` skill, which the `planning-worker` contract cites instead of owning, gives every
executor the same steps and leaves one place to change them. The split follows
`ADR-executor-neutral-planning-steps-in-a-spec-reference`; the size follows
`ADR-planning-reference-fits-the-existing-byte-budgets`.

## 2. User Stories

- **US-1**: As a Host running a proposal's Planning in `direct` mode, I want the ordered Planning steps in a `spec`
  skill reference, so that I follow the same procedure a `planning-worker` follows without reading a subagent prompt.
- **US-2**: As a maintainer of the Planning procedure, I want the steps in exactly one file, so that a change cannot
  drift between two copies.

## 3. Non-Goals

1. **Scope Excluded**: changing what a Planning step requires. The steps move with their wording; no step is added,
   dropped or reworded beyond the address to the executor and the links the new location needs.
2. **Scope Excluded**: CLI, schema, workflow definition or envelope-mechanics changes (`worker-records.md` stays the
   source for envelope mechanics and is cited, not restated).
3. **Scope Excluded**: the Planning-step edits of `PROP-envelope-record-gaps`; that proposal adapts to the steps'
   final place when it lands second.
4. **Scope Excluded**: trimming another `spec` reference to make room.
   - **When to Reconsider**: the reference grows past about 8 KB (`ADR-planning-reference-fits-the-existing-byte-budgets`).

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] A direct Host reaches the Planning steps from the spec skill
- **Given** the `spec` skill's routing table
- **When** a Host reads the `proposal` row to run Planning in `direct` mode
- **Then** the row links `references/planning.md`, and that reference holds the ordered steps: first-turn
  `status: reviewing` with its commit and the `needs_decompose` return, answers recorded in a commit of their own
  before they are folded, PADRs with `--summary`, the review depth per effort citing `review-loop.md`, the
  support-role envelopes, questions in one round, the `dev_effort` check, observed feedback, the `collect-feedback`
  sweep and the single `worker` envelope

### [AC-02] The planning-worker contract cites the reference and keeps only worker obligations
- **Given** the `planning-worker` contract
- **When** a worker reads its `## Procedure`
- **Then** it holds the worktree and `git -C <worktree>` rule, the nested-role rule (start, wait, never end while one
  runs) and one step that follows `.devkit/managed/spec/skills/spec/references/planning.md`; `## Input`, `## Return`
  with `final_head`, `## Write boundaries` and `## On a problem` are unchanged, and none of the moved steps' sentences
  remain in the contract

### [AC-03] Every moved step survives the move
- **Given** the contract's steps 2 to 6 at the base `d981971`
- **When** they are compared with `references/planning.md` and the new contract
- **Then** each sentence appears in exactly one of the two files, and `packages/devkit-spec/tests/test_role_contracts.py`
  pins the moved phrases in the reference (`Collect the questions for the user in one round, never stopping at the
  first`, `as a commit of their own`, `status: reviewing`, `needs_decompose: true`, `never into a file of their own`,
  `envelope answer --unit <proposal dir> --answers-to <worker-NN.yaml>`) and asserts that the contract no longer holds them

### [AC-04] The byte budgets hold without trimming
- **Given** `packages/devkit-spec/tests/test_bundle_budgets.py`
- **When** `just test devkit-spec` runs
- **Then** `references/planning.md` is under 12288 bytes, `spec/SKILL.md` under 11776 bytes, every `spec` reference
  is linked from its skill, and no other `spec` reference changes

### [AC-05] The Living Spec says where the Planning procedure lives
- **Given** `CAP-DLV-delivery-workflows` §4.6
- **When** a reader looks up the `planning-worker` row and the sentence on where a role's procedure lives
- **Then** the row names `spec/references/planning.md` as the procedure's place and the sentence no longer lists the
  `planning-worker` among the roles whose procedure lives in the contract

## 5. Assumptions

- The reference addresses "you" as the executor of the Planning turn (the `direct` Host or the `planning-worker`),
  per the ADR. The moved step 6 keeps its `worker` envelope command; a `direct` Host writes the same single `worker`
  envelope for its run, as `worker-records.md` already requires of every run.
- `test_every_restatement_cites_the_loop` keeps the contract in `CITING` only while the contract names
  `review-loop.md`; the depth step that cites it moves, so the reference replaces the contract in `CITING`.
- The `Planning returns follow per-run feedback` line at the end of `spec/SKILL.md` stays: it is the skill-level
  pointer for returns and is not a contract step.
- The proposal's premises hold at base `d981971`: `spec/SKILL.md` is 6531 bytes, the contract 7953 bytes, and no
  other unit has edited the contract's steps yet.
