---
id: UC-advance-an-idea
aliases:
  - UC-incubate-an-idea
title: Advance an idea and leave resumable current context
summary: "An AI coding agent advances one useful product action through adaptive-development guidance and leaves current facts, executable instructions and honest evidence for the next action or session."
area: delivery
primary_actor: AI coding agent
supporting_actors: [Product owner, Optional support and reusable execution agents]
status: active
capabilities:
  - CAP-DLV-adaptive-development
  - CAP-DLV-adaptive-assignments
  - CAP-HARN-agent-guidance
entrypoints:
  - packages/devkit-adaptive/src/devkit_adaptive/bundles/adaptive_dev/bundle/skills/adaptive-dev/SKILL.md
  - packages/devkit-adaptive/src/devkit_adaptive/bundles/adaptive_dev/bundle/skills/adaptive-dev/references/orchestration.md
  - packages/devkit-adaptive/src/devkit_adaptive/features/assignment/cli/commands.py
---

# [UC-advance-an-idea] Advance an idea and leave resumable current context

## 1. Goal

- **Goal**: advance the next useful product action and retain enough current facts to resume it without delivery history.
- **Scope**: adaptive-development agent guidance; one discovery, research, implementation or verification action in one sitting.
- **Trigger**: the product owner invokes adaptive-development work or asks the agent to resume an idea.
- **Preconditions**: the `adaptive-dev` bundle and the repository's ordinary execution environment are available.

## 2. Main Success Scenario

1. The agent invokes adaptive-development guidance for the requested product action (`CAP-DLV-adaptive-development`, `CAP-HARN-agent-guidance`).
2. The agent verifies that the effective development approach permits adaptive-development work (`CAP-DLV-adaptive-development`).
3. The agent recovers current goals, choices and execution evidence from available context and implementation (`CAP-DLV-adaptive-development`).
4. The agent selects the next useful action from the remaining decision or evidence need (`CAP-DLV-adaptive-development`).
5. The agent performs that bounded product action inside the agreed goal and constraints (`CAP-DLV-adaptive-development`).
6. The agent verifies the retained result against intended usage and applicable project checks (`CAP-DLV-adaptive-development`).
7. The agent updates current resume facts and reports observed outcomes, limitations and the next action (`CAP-DLV-adaptive-development`).

## 3. Extensions

- **2a.** SDD approach: the agent stops product work and explains the shared configuration action; the use case ends without changing approach.
- **2b.** Unreadable policy: inspection reports its actual error, including `DEVELOPMENT_CONFIG_INVALID` for an invalid approach; the agent reports the configuration action and the use case ends.
- **3a.** Missing or stale context: the Host runs `uv run devkit adaptive assignment list` and treats every open assignment as interrupted; the agent recovers current facts from source/run instructions and missing product answers without reconstructing discarded history; resumes at step 4.
- **3b.** A retained research material exists: the agent reads it by the `MAT-<slug>` ID the user supplies or the current context links, never starting or suggesting a research entry; resumes at step 4.
- **4a.** Missing product decision: the agent asks only the missing next-action question with its supported recommendation; awaits the product owner's decision, then resumes at step 4.
- **5a.** Goal or constraint change: the agent obtains the product owner's direction before dependent work; resumes at step 4 with the settled direction or ends while that decision is pending.
- **5b.** Optional support: the agent delegates a separable question or usage or implementation scope with source/base identity, absolute ownership, permitted actions/Git, checks, stop condition and return fields, records the assignment before dispatch and verifies the return with `CAP-DLV-adaptive-assignments`, checks actual paths and evidence and folds it into current choices; resumes at step 6.
- **5b5.** Shared interface: if delegated deliverables depend on an unsettled interface, the coordinator assigns its owner and resolves it before concurrent dependent writes or sequences them. It supplies the agreed identity to dependent assignments and reassesses them if it changes. An interface that outlives its assignment is first recorded in its current-state document, marked as agreed until its implementation is integrated; that document's ID and source identity then identify it; resumes at step 5.
- **5b1.** Optional role lead: if useful and supported within the Host-wide allowance, the lead delegates narrowed children at depth at most Host → lead → child, counts waiting leads and verifies its aggregate scope; a swarm-worker lead records children with its parent ID and closes them before returning; the Host records children of planner or verifier leads or leaves them unrecorded; resumes at step 6.
- **5b2.** Missing nesting or unknown/exhausted capacity: the Host uses direct, flat or sequential execution with the same result/check contract and no host-setting change; resumes at step 5.
- **5b3.** Concurrent writers: the Host assigns separate worktrees and exclusive ownership; parents wait before writing in child-owned checkouts. If isolation is unavailable, writers run serially; resumes at step 6.
- **5b4.** Incompatible overlay or unavailable registered invocation: the Host reports the gap, rejects expanded permissions and selects compatible direct execution or explicitly labelled emulation; resumes at step 5.
- **5b6.** Governing documents: before partitioning a multi-writer build, the coordinator finds the documents that govern the goal and names them in each assignment by ID or absolute path, or `none`. Recording passes them as `--governing` and refuses unresolved values. An assignee treats them as constraints and returns a conflict to the Host instead of resolving it; resumes at step 5.
- **5c.** Failed or out-of-scope role result: the agent reports actual partial state and rejects a failed assignment verification with its codes as completion evidence; resumes at step 4 without discarding another actor's work.
- **6a.** Failed retained or combined behavior: the Host routes reproducing evidence to the responsible writer for bounded repair, repeats combined checks and reports an unresolved result at the stop condition; resumes at step 6.
- **6a1.** Probe fails before valid product execution: the agent classifies a harness or environment cause only on evidence, otherwise keeps the cause unknown and product behavior unverified; resumes at step 6 after a valid probe is available.
- **6a2.** Identical repair attempts produce no new diagnostic evidence: the agent changes strategy at the applicable bound, or reports an unresolved blocker when the needed next action is unavailable; resumes at step 6 or proceeds to step 7.
- **6b.** Missing verification evidence: the agent reports the check as unverified and records the gap/next action without claiming successful retained behavior; proceeds to step 7 with that limitation.
- **6c.** Retained result integrated: the Host updates the current-state documents the subject warrants, describing current state and writing nothing for a discarded experiment, and includes `uv run devkit rules check` on changed documents and any project-defined document checks in combined checks; an unavailable document check is reported as unverified; resumes at step 6.
- **7b.** Failure/interruption: the Host collects or stops children, preserves dirty/unmerged results and active ownership, and writes source identity, failed checks, outstanding ledger IDs and next recovery action to current context before cleanup; the use case pauses.
- **7a.** Explicit SDD adoption request: the agent explains preparing SDD assets while adaptive development remains active and routes to the separately available baseline procedure; this use case ends without activating SDD.
- **7c.** Retained behavior, structure or choice: the Host maps each one in current context to its document ID, or its path where the document has no ID, or marks it `undocumented`, linking rather than copying content; a project that has no document yet records that fact and gets no seeded tree; resumes at step 7.

## 4. Postconditions

- **Success guarantee**: the bounded action has an observed outcome, relevant current facts and execution instructions are retained, and limitations or the next action are explicit.
- **Minimal guarantee**: no implicit approach switch, invented product decision or skipped-as-passed check is claimed; unrelated edits and existing SDD history are preserved.

## 5. Acceptance Criteria (Given / When / Then)

Rules: approach-gated entry; adaptive next action; bounded evidence; goal-bound iteration; optional role boundaries;
truthful verification; mutable coordinator-owned resume facts; useful alternatives; voluntary adoption;
current-state project documents.

### Scenario 1: Advance a representative flow

- **Covers**: main success scenario
- **Given**: a partial product goal, known local-use constraints and effective adaptive development.
- **When**: the agent advances a representative implementation action.
- **Then**: the flow is actually exercised, current context records source-specific evidence and no per-change SDD Unit is created.

### Scenario 2: Stop under SDD or invalid policy

- **Covers**: 2a, 2b
- **Given**: effective SDD or an invalid shared approach.
- **When**: the `/adaptive-dev` entry inspects policy.
- **Then**: product files and current context remain unchanged, and the actual configuration action/error is reported.

### Scenario 3: Recover and clarify only missing facts

- **Covers**: 3a, 4a
- **Given**: absent/stale context and a product fact needed for the next action.
- **When**: the agent resumes.
- **Then**: it reads current implementation, reuses known answers and asks the missing question without requiring a complete backlog or history.

### Scenario 4: Keep changes inside the settled goal

- **Covers**: 5a
- **Given**: a proposed change to the product goal or constraints.
- **When**: the agent identifies the change.
- **Then**: dependent work waits for product direction; implementation reconstruction inside the unchanged goal needs no SDD records.

### Scenario 5: Validate optional support

- **Covers**: 5b, 5c
- **Given** a recorded assignment with bounded write authority and an assignee return containing out-of-scope changes,
- **When** the Host records the return and runs `uv run devkit adaptive assignment verify <id>`,
- **Then** `result=fail` and `ADAPTIVE_SCOPE_VIOLATION` reject the return; if a command cannot record, the Host retains manual payload, diff and checkpoint checks and reports the assignment as unrecorded.

### Scenario 6: Report verification truthfully

- **Covers**: 6a, 6b
- **Given**: failed intended behavior or an unavailable required check.
- **When**: the agent verifies the action.
- **Then**: it repairs and reruns affected checks where possible, while missing evidence remains an explicit limitation.

### Scenario 7: Keep adoption voluntary

- **Covers**: 7a
- **Given**: an explicit request to adopt SDD after adaptive development.
- **When**: the agent presents the transition doorway.
- **Then**: package/asset preparation is distinguished from baseline readiness and activation; this use case changes no approach.

### Scenario 8: Read retained research by its ID

- **Covers**: 3b
- **Given**: current context links a committed research material by its ID.
- **When**: the agent recovers current facts.
- **Then**: it reads that material as evidence and neither invokes nor suggests a research entry.

### Scenario 9: Isolate writers and check their aggregate

- **Covers**: 5b1, 5b2, 5b3, 5b4, 6a, 7b
- **Given**: two separable writing assignments and a shared product constraint.
- **When**: isolated workers pass locally but their combined result fails or work is interrupted.
- **Then**: the Host retains exact source-specific outcomes, routes bounded repair and preserves dirty/unmerged checkpoints; no worker pass substitutes for combined or applicable landed-target verification.

### Scenario 10: Diagnose a failed probe and preserve recovery

- **Covers**: 6a1, 6a2, 7b
- **Given**: a fixture fails twice with the same import error before product execution and no material new evidence.
- **When**: the coordinator assesses the failure and checkpoints before interruption.
- **Then**: product behavior remains unverified, diagnosis changes before an equivalent retry, and useful recovery facts remain available for applicability checks on resume.

### Scenario 11: Resolve a shared interface before concurrent work

- **Covers**: 5b5
- **Given**: two disjoint writing assignments depend on an unsettled API.
- **When**: the coordinator prepares their handoffs.
- **Then**: it assigns the API owner, resolves the interface or sequences the work, and supplies its identity to dependents.

### Scenario 12: Link a multi-writer build to project documents

- **Covers**: 5b6, 6c, 7c
- **Given**: a project with an architecture document and two writing assignments; one retained behavior has no document.
- **When**: the coordinator partitions the build, integrates the retained results and updates current context.
- **Then**: each assignment names its governing documents, the changed structure is described in the architecture document as current state, the project's document checks run with the combined checks, and current context maps each retained item to a document ID or `undocumented` without a per-change record.

### Resume from recorded assignments

- **Covers**: 3a, 7b
- **Given** outstanding assignments recorded before an interruption,
- **When** the Host resumes,
- **Then** it reads list/show repository facts and records a return, dispatches again or closes each assignment; if a command cannot record it preserves manual payload/diff/checkpoint evidence and reports unrecorded work.
