---
id: SPEC-direct-planning-procedure
title: Planning procedure reachable from the spec skill for any executor
summary: Moves the ordered Planning steps out of the planning-worker contract into a spec skill reference that direct-mode Hosts and workers both follow, so the procedure lives in one place.
status: planned
created: 2026-10-19
related_capabilities: []
related_stories: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-direct-planning-procedure] Planning procedure reachable from the spec skill for any executor

## 1. Problem Statement & Motivation

Handed off from proposal PROP-direct-planning-procedure on 2026-10-19.

### 1. Background & Hypothesis

- **Problem**: The `spec` skill's routing table says Planning "runs on `plan-<slug>` to `plan-accept`", and
  `effort.md` gives the review depth per effort, but the ordered Planning steps (set `status: reviewing` and commit,
  record decisions as PADRs, gather questions in one round, update `dev_effort`, sweep feedback, end with one `worker`
  envelope) are written only in the `planning-worker` role contract. A Host running Planning in `direct` mode has to
  read a subagent contract written for another actor (`FB-direct-planning-procedure-location`).
- **Hypothesis**: One Planning reference in the `spec` skill, which the `planning-worker` contract cites instead of
  owning, gives every executor the same steps and leaves one place to change them.

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Planning procedure reachable from the spec skill for any executor so that system capabilities are extended.

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

- **Q1**: Which steps are executor-neutral and move to the reference, and which stay in the role contract (nested
  delegation, returning the head to the Host)?
- **Q2**: Can the move fit the existing bundle byte budgets of the `spec` skill and the role contract, or does another
  reference need trimming?

### 3. Proposed Design & Impact

- **Q1** (`ADR-executor-neutral-planning-steps-in-a-spec-reference`): a new `spec` skill reference
  `references/planning.md`, linked from the routing table's proposal row, holds the executor-neutral steps of the
  contract's steps 2 to 6: first-turn `status: reviewing` and the `needs_decompose` return, answers recorded before
  they are folded, PADRs with a summary, review depth per effort (citing `effort.md` and `review-loop.md`) and the
  support-role envelopes, one round of questions, the `dev_effort` check, observed feedback, the sweep and the single
  `worker` envelope. It addresses the `direct` Host and the worker alike and cites `worker-records.md` for envelope
  mechanics. The `planning-worker` contract keeps the worktree and `git -C` rule, nested roles (start, wait, never end
  while one runs), Input, Return with `final_head`, Write boundaries and On a problem, and points to the reference by
  its managed path. The steps move; nothing is copied.
- **Q2** (`ADR-planning-reference-fits-the-existing-byte-budgets`): the reference is about 4.5 KB against the
  12288-byte skill document budget and the link keeps `spec/SKILL.md` near 6.6 KB of its 11776; role contracts have
  no budget and the contract shrinks to about 4 KB. No other reference is trimmed.
- Affected: `packages/devkit-spec` bundle (`skills/spec/SKILL.md`, the new `skills/spec/references/planning.md`,
  `subagents/planning-worker.md`); tests that pin contract phrases (`tests/test_role_contracts.py`,
  `tests/test_effort_procedure.py` `CITING`); `CAP-DLV-delivery-workflows` (the `planning-worker` row of the role
  table and the sentence on where a worker's procedure lives), so `boundaries.owns` adds `delivery/`.
  `CAP-HARN-agent-guidance` lists asset ids only and is unchanged. No CLI or schema change.
- **Development effort `medium`** (was `low`): the move changes the accepted `CAP-DLV-delivery-workflows` statement that the
  `planning-worker` procedure is in its contract, the default case for `medium` in `effort.md`; one `code-reviewer`
  pass checks that no step was dropped or reworded in the move.
- **Order with `PROP-envelope-record-gaps`**: that proposal changes the `planning-worker` contract and `review-loop.md`
  in Development. Whichever lands second adapts its edits to the other; if this one lands first, the Planning-step
  edits of `PROP-envelope-record-gaps` go into `references/planning.md` rather than the contract. Recommended order:
  this one first (size S), so the other edits the steps in their final place.

### 4. Lifecycle & Retirement Criteria

- Preliminary decisions: `devkit spec proposal padr direct-planning-procedure "<title>"`.
- On acceptance (`plan-accept`): hand off with `devkit spec proposal handoff direct-planning-procedure`.
- On rejection: `status: rejected` with the user's reason in the commit message.

