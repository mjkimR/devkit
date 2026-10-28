---
id: UC-speed-up-selected-slow-operations
title: Speed Up Selected Slow Operations
summary: "A developer has an AI coding agent measure selected slow operations, decide the attributed speedup candidates in one round, and apply only agreed behavior-preserving changes with per-change measurement and differential evidence, ending with a final interleaved measurement."
area: governance
primary_actor: Developer
supporting_actors:
  - AI coding agent running the performance-pass playbook
  - Subagents for agreed edits in isolated checkouts, where the host supports them
  - Fresh reviewer of the work item's diff
status: active
capabilities:
  - CAP-DIST-context-and-playbooks
  - CAP-DLV-performance-pass
created_at: 2026-10-28
---

# [UC-speed-up-selected-slow-operations] Speed Up Selected Slow Operations

## 1. Goal

- **Goal**: make the operations the developer selects measurably faster, or lighter in subprocesses or memory,
  without changing their observable behavior, so that every reported saving survives repetition and no contract
  changes unnoticed
- **Scope**: the `performance-pass` playbook of the opt-in `maintenance` catalog bundle, run by an AI coding agent
  with the repository's tools, its feature workflow, the application procedure of the co-deployed `review-refactor`
  playbook and the repository's integration path
- **Trigger**: an operation feels slow, or before a release, the developer invokes the playbook or confirms it when
  `spec` intake offers it
- **Preconditions**: the `maintenance` bundle is installed with `all` or `performance`

---

## 2. Main Success Scenario

1. The developer invokes the performance-pass playbook, which loads on demand (`CAP-DIST-context-and-playbooks`,
   `CAP-DLV-performance-pass`).
2. The agent records the intake with the environment, and the developer selects each target operation with its exact
   command, metric and optional goal (`CAP-DLV-performance-pass`).
3. The agent measures each target's baseline unprofiled, with warm-up and interleaved repetitions on a quiet machine,
   and records it (`CAP-DLV-performance-pass`).
4. The agent attributes the cost, profiling only to locate it and confirming each share unprofiled
   (`CAP-DLV-performance-pass`).
5. The agent records each candidate with its measured share, expected saving, risk and classification, and resolves
   `review-refactor` by exact retrieval to read its application sections as reference text
   (`CAP-DLV-performance-pass`, `CAP-DIST-context-and-playbooks`).
6. The agent presents every candidate in one decision round with the route and edited paths; the developer decides
   each one (`CAP-DLV-performance-pass`).
7. The agent applies the agreed behavior-preserving changes as one work item through the repository's feature
   workflow, following `review-refactor`'s application procedure, and commits each change with its measured before
   and after and its differential evidence (`CAP-DLV-performance-pass`).
8. A fresh reviewer, briefed with each change's classification and claim of equal behavior, looks for inputs that
   break it; the agent then measures every target interleaved against the intake revision in one session
   (`CAP-DLV-performance-pass`).
9. The agent completes the run report with baselines, coverage, candidates, changes, decisions, follow-ups, the final
   measurement and the integration state; with no decision pending, the run is complete (`CAP-DLV-performance-pass`).

---

## 3. Extensions

- **2a.** A target's command, metric or working directory is missing: the agent clarifies it before any timed run;
  resumes at step 2.
- **3a.** The machine is loaded or another workload of the run was active during a measurement: the agent records
  the load and re-measures later; resumes at step 3.
- **3b.** One outlier decides whether a difference exceeds the noise floor: the agent adds five repetitions per
  variant before concluding; resumes at step 4.
- **5a.** A candidate's expected saving is below the noise floor: it is dropped and counted in the coverage;
  resumes at step 6.
- **5b.** A measured cost no change can remove: it is reported as kept with its reason; resumes at step 6.
- **5c.** A heading the playbook cites is missing from the resolved `review-refactor` file: the run stops with a
  report naming the missing section and applies nothing; the use case ends.
- **6a.** The run is in `survey` mode and the developer approves no change: the run stops at the decision round with
  nothing applied; resumes at step 9.
- **6b.** The run is unattended or the developer answers nothing: the run stops with candidates pending and nothing
  applied; resumes at step 9.
- **6c.** The developer approves a contract-changing speedup: it becomes its own work item through the normal
  development workflow; resumes at step 7 for the behavior-preserving changes.
- **6d.** The developer defers or keeps a candidate: the deferral names a destination and restart condition, the keep
  its reason; resumes at step 7.
- **7a.** The host has no subagents: the agent applies the changes itself one after another; resumes at step 7.
- **7b.** The differential comparison shows a difference: the agent fixes it, or returns the change to the decision
  round as its own contract-change work item; resumes at step 7.
- **8a.** The reviewer reproduces an input under which behavior differs: the agent fixes the change, or returns it to
  the decision round as its own contract-change work item; resumes at step 8.
- **8b.** The host has no subagents: the agent reviews the work item's diff itself and records the review as a
  self-review; resumes at step 8.

---

## 4. Postconditions

- **Success guarantee**: every applied change is agreed, classified behavior-preserving, committed alone with its
  measured before and after and differential evidence, reviewed and integrated after its own approval; every
  reported saving comes from unprofiled, interleaved runs in one session, and the report records the final
  measurement against the intake revision, coverage, follow-ups and the integration state.
- **Minimal guarantee**: invocation and measurement apply nothing; no contract-changing speedup is applied as
  behavior-preserving, no profiler figure is reported as a saving, `review-refactor`'s own intake and decision rounds
  never start, and the working checkout is never stashed or switched.

---

## 5. Acceptance Criteria (Given / When / Then)

### Scenario 1: Applies an agreed speedup with measured evidence
- **Covers**: main success scenario
- **Given**: a selected command whose file listing repeats work, and an approved candidate that removes the
  repetition
- **When**: the agent applies the work item
- **Then**: the change is committed alone with median, minimum and range for old and new from interleaved runs and a
  differential comparison over the corpus and error cases, and the report records the final measurement against the
  intake revision

### Scenario 2: Clarifies a missing target before timing
- **Covers**: 2a
- **Given**: an invocation that names no command to measure
- **When**: the agent records the intake
- **Then**: the agent asks for the exact command, metric and working directory and takes no timed run until they are
  recorded

### Scenario 3: Re-measures under load
- **Covers**: 3a
- **Given**: a verification run of the work item active during a comparison
- **When**: the agent records the load before and after
- **Then**: the comparison is discarded and repeated once no workload of the run is active

### Scenario 4: Drops a candidate below the noise floor
- **Covers**: 5a
- **Given**: a candidate whose expected saving is smaller than the noise floor
- **When**: the agent prepares the decision round
- **Then**: the candidate is dropped, counted in the coverage and never presented for approval

### Scenario 5: Stops on a missing cited heading
- **Covers**: 5c
- **Given**: a `review-refactor` override that renamed "Commits and verification"
- **When**: the agent resolves `review-refactor` before the decision round
- **Then**: the run stops with a report naming the missing section, and nothing is applied

### Scenario 6: Stops a survey at the decision round
- **Covers**: 6a
- **Given**: a `survey` run over three operations
- **When**: the developer approves no change in the decision round
- **Then**: the report records the ranked candidates with outcome `stopped at decision round`, and no file other than
  the run report changes

### Scenario 7: Stops an unattended run at the decision round
- **Covers**: 6b
- **Given**: an external runner invokes the playbook with no developer present
- **When**: the candidates are ready
- **Then**: the report records them as pending with outcome `stopped at decision round`, and nothing is applied

### Scenario 8: Routes a persistent cache separately
- **Covers**: 6c
- **Given**: a candidate that adds a cache file kept between runs
- **When**: the developer approves it
- **Then**: it is classified a contract change and becomes its own work item through the normal development
  workflow, outside the behavior-preserving work item

### Scenario 9: Applies changes sequentially without subagents
- **Covers**: 7a
- **Given**: two agreed changes and a host without subagents
- **When**: the agent applies the work item
- **Then**: the agent applies them one after another, and each commit holds one change with its own measurement

### Scenario 10: Treats a differential difference as a contract change
- **Covers**: 7b
- **Given**: a replaced scan call that raises on a symbolic link loop where the old call returned a value
- **When**: the differential comparison runs over the error cases
- **Then**: the change is fixed, or it returns to the decision round as a contract-change work item; it is never
  kept as an approved behavior change inside the behavior-preserving work item

### Scenario 11: Fixes a breaking input the reviewer reproduces
- **Covers**: 8a
- **Given**: a reviewer brief carrying each change's classification, the error paths of replaced APIs and the memo
  keys
- **When**: the reviewer reproduces an input under which a memo returns a stale answer
- **Then**: the change is fixed or returned to the decision round before the work item is reported
