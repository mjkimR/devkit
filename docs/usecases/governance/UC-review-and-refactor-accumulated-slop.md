---
id: UC-review-and-refactor-accumulated-slop
title: Review and Refactor Accumulated Slop
summary: "A developer has an AI coding agent review selected code, guidance or CLI surfaces for accumulated maintenance cost, decide the evidenced findings one surface batch at a time, and apply only the agreed consolidations and reductions with preservation evidence in parallel isolated checkouts."
area: governance
primary_actor: Developer
supporting_actors:
  - AI coding agent running the review-refactor playbook
  - Subagents for parallel review and for agreed edits in isolated checkouts, where the host supports them
  - Fresh reviewer of the work item's diff
status: active
capabilities:
  - CAP-DIST-context-and-playbooks
  - CAP-DLV-review-refactor
created_at: 2026-10-26
---

# [UC-review-and-refactor-accumulated-slop] Review and Refactor Accumulated Slop

## 1. Goal

- **Goal**: shrink the code, agent guidance and CLI surface the developer selects by consolidating duplicated logic
  and removing what is unneeded, with every change evidenced and agreed, so that accumulated agent-added slop stops
  raising maintenance cost
- **Scope**: the `review-refactor` playbook of the opt-in `maintenance` catalog bundle, run by an AI coding agent
  with the repository's tools, its refactor and development workflows and its integration path
- **Trigger**: before a release, after substantial feature growth or on request, the developer invokes the playbook
  or confirms it when `spec` intake offers it
- **Preconditions**: the `maintenance` bundle is installed with `all`, `upkeep` or `refactoring`

---

## 2. Main Success Scenario

1. The developer invokes the review-refactor playbook, which loads on demand (`CAP-DIST-context-and-playbooks`,
   `CAP-DLV-review-refactor`).
2. The agent records the intake and the developer selects the surfaces and roots; the agent splits the run into one
   batch per surface (`CAP-DLV-review-refactor`).
3. The agent reviews one batch against the surface's review questions, using subagents for parallel review where
   the host supports them and validating each result at its cited location (`CAP-DLV-review-refactor`).
4. The agent records each finding with its location, review question, named maintenance cost and proposed
   disposition, and drops candidates without a named cost (`CAP-DLV-review-refactor`).
5. The agent presents the batch's findings in one decision round with each change's route and edited paths; the
   developer decides each one (`CAP-DLV-review-refactor`).
6. The agent applies the agreed behavior-preserving changes as one direct-mode work item on its own branch:
   subagents edit the changes with disjoint write scopes in parallel, each in its own isolated checkout prepared like
   a fresh checkout, and leave their results uncommitted (`CAP-DLV-review-refactor`).
7. The agent moves each result onto the branch one at a time and commits it alone through the repository's commit
   checks with its preservation evidence, including a side-by-side comparison of the old and new code where the
   inputs can be enumerated, and runs the full verification at the final head (`CAP-DLV-review-refactor`).
8. A fresh reviewer, briefed with each change's preservation claim, looks for inputs that break it; the agent fixes
   its findings and reports the work item, which integrates after its own approval (`CAP-DLV-review-refactor`).
9. The agent completes the run report with coverage, findings, changes, behavior changes, decisions, follow-ups,
   counts and the integration state; with no decision pending, the batch is complete (`CAP-DLV-review-refactor`).

---

## 3. Extensions

- **2a.** Surfaces or roots are missing: the agent clarifies them before inspecting; resumes at step 2.
- **3a.** The host has no subagents: the agent runs the same review itself; resumes at step 4.
- **3b.** A subagent claim does not hold at the cited location, or a root's result lists nothing read: the agent
  drops the claim or records a coverage gap; resumes at step 4.
- **4a.** A finding lands on an unselected surface: it is deferred with a follow-up; if the developer adds the
  surface, a new batch with its own roots and decision round follows; resumes at step 5.
- **4b.** A finding is a mismatch against agreed documentation: it is deferred with a follow-up naming drift
  reconciliation; resumes at step 5.
- **5a.** The run is unattended or the developer answers nothing: the run stops with findings pending and nothing
  applied; resumes at step 9.
- **5b.** The developer approves a contract removal: it becomes its own work item through the normal development
  workflow; resumes at step 6 for the behavior-preserving changes.
- **5c.** The developer defers or keeps a finding: the deferral names a destination and restart condition, the keep
  its reason; resumes at step 6.
- **5d.** A proposed consolidation joins implementations that do not behave identically: the finding lists each
  difference with the behavior the consolidation keeps, and the developer's decision covers each; resumes at step 6.
- **6a.** Every edited source file lies in one feature or module: the work item follows the feature workflow at its
  own depth; resumes at step 8.
- **6b.** A subagent's edit leaves its assigned scope or departs from the agreed change: the agent reverts the hunks
  and redoes the change or returns it to the decision round; resumes at step 6.
- **6c.** The run is a seeded exercise: decisions are labeled simulated and change only the fixture; resumes at
  step 9.
- **6d.** Two changes' write scopes overlap or one change builds on another: the agent applies them one after another
  on the previous checkpoint; resumes at step 7.
- **6e.** The host has no subagents: the agent applies the changes itself one after another; resumes at step 7.
- **6f.** A subagent's change fails a layering, rule or configuration check: the subagent reports the failure without
  adding an exception, ignore entry, rule setting or check bypass, and the agent resolves the placement or returns
  the change to the decision round; resumes at step 6.
- **7a.** The side-by-side comparison shows a difference: the agent fixes it, or the developer approves it as a
  behavior change recorded in the report; resumes at step 7.
- **7b.** A removal leaves branches, parameters, types, errors or helpers that only the removed path reached: the
  agent removes those within the agreed change and records each one it keeps or defers; resumes at step 7.
- **8a.** The host has no subagents: the agent reviews the work item's diff itself and records the review as a
  self-review; resumes at step 8 with the fixes.
- **8b.** The reviewer reproduces an input under which behavior differs: the agent fixes the change, or the developer
  approves the difference as a behavior change; resumes at step 8.
- **9a.** The report was written before the work item integrated: the agent updates its outcome with the integration
  state when the work item integrates or stops; the use case ends.

---

## 4. Postconditions

- **Success guarantee**: every applied change is agreed, committed alone through the commit checks with reachability,
  before-and-after verification and, where its inputs can be enumerated, a side-by-side comparison, reviewed and
  integrated after its own approval; the report separates findings from changes, lists approved behavior changes
  apart from inputs no longer accepted, and names coverage, gaps, follow-ups, counts and the integration state.
- **Minimal guarantee**: invocation applies nothing; no change lands outside the batch's write scope, no contract
  change is presented as refactoring, no governance check is relaxed to make a change pass, and a batch never claims
  the whole repository reviewed.

---

## 5. Acceptance Criteria (Given / When / Then)

### Scenario 1: Applies an agreed consolidation with evidence
- **Covers**: main success scenario
- **Given**: a selected code root with duplicated behavior in two callers
- **When**: the developer approves its consolidation in the decision round
- **Then**: the change is committed alone on the work item's branch with reachability evidence and verification
  before and after, and the helper sits at the lowest common owner

### Scenario 2: Clarifies missing scope first
- **Covers**: 2a
- **Given**: an invocation that names no surface
- **When**: the agent records the intake
- **Then**: the agent asks for surfaces and roots and inspects nothing until they are recorded

### Scenario 3: Drops an unconfirmed subagent claim
- **Covers**: 3b
- **Given**: a subagent reports an unused function that a registry still references
- **When**: the agent validates the claim at its location
- **Then**: the claim is dropped or recorded as a coverage gap and never enters the decision round

### Scenario 4: Defers a finding on an unselected surface
- **Covers**: 4a
- **Given**: a code batch whose finding would change CLI help, with the CLI surface unselected
- **When**: the agent records the finding
- **Then**: it is deferred with a follow-up and nothing is applied for it

### Scenario 5: Stops an unattended run at the decision round
- **Covers**: 5a
- **Given**: an external runner invokes the playbook with no developer present
- **When**: the batch's findings are ready
- **Then**: the report records them as pending with outcome `stopped at decision round`, nothing is applied, and no file other than the run report changes

### Scenario 6: Routes a contract removal separately
- **Covers**: 5b
- **Given**: an unneeded command option the developer approves for removal
- **When**: the agent applies the batch
- **Then**: the removal is its own development work item with contract and documentation updates, and the batch's
  refactor work item does not contain it

### Scenario 7: Reverts an out-of-scope subagent edit
- **Covers**: 6b
- **Given**: a subagent edit that touches a path outside its assigned scope
- **When**: the agent checks the diff
- **Then**: the hunks are reverted without resetting other scopes' paths, and the change is redone or returned to the
  decision round

### Scenario 8: Changes only the fixture in an exercise
- **Covers**: 6c
- **Given**: a seeded fixture repository and simulated decisions
- **When**: the agent applies the changes
- **Then**: the decisions are labeled simulated and only the fixture changes

### Scenario 9: Applies disjoint changes in parallel checkouts
- **Covers**: main success scenario
- **Given**: three agreed changes with disjoint write scopes and a host with subagents
- **When**: the agent applies the work item
- **Then**: each change is edited in its own isolated checkout prepared like a fresh checkout, and the branch receives
  three commits, each holding one change with its own evidence

### Scenario 10: Applies overlapping changes one after another
- **Covers**: 6d
- **Given**: two agreed changes that edit the same file
- **When**: the agent plans the edit tasks
- **Then**: the second change starts from the checkpoint the first one committed

### Scenario 11: Refuses a governance exception from an editing subagent
- **Covers**: 6f
- **Given**: a subagent change that fails a layering check
- **When**: the subagent returns its result
- **Then**: the result reports the failure, the diff adds no exception, ignore entry, rule setting or check bypass,
  and the change is re-placed or returned to the decision round

### Scenario 12: Records a differential comparison for a replaced parser
- **Covers**: 7a
- **Given**: a change that replaces a parser and the old parser run from an extracted copy
- **When**: the agent records the change's preservation evidence
- **Then**: the record names the input count and the result over the repository's corpus plus edge cases, and each
  difference is fixed or recorded as an approved behavior change

### Scenario 13: Fixes a breaking input the reviewer reproduces
- **Covers**: 8b
- **Given**: a reviewer brief carrying each change's preservation claim
- **When**: the reviewer reproduces an input under which the new code behaves differently
- **Then**: the change is fixed or the difference is approved as a behavior change before the work item is reported
