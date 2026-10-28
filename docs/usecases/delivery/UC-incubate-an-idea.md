---
id: UC-incubate-an-idea
title: Advance an idea and leave resumable current context
summary: "An AI coding agent advances one useful product action through incubation guidance and leaves current facts, executable instructions and honest evidence for the next action or session."
area: delivery
primary_actor: AI coding agent
supporting_actors: [Product owner, Optional product clarification/research/usage subagents]
status: active
capabilities:
  - CAP-DLV-idea-incubation
---

# [UC-incubate-an-idea] Advance an idea and leave resumable current context

## 1. Goal

- **Goal**: advance the next useful product action and retain enough current facts to resume it without delivery history.
- **Scope**: incubation agent guidance; one discovery, research, implementation or verification action in one sitting.
- **Trigger**: the product owner invokes incubation work or asks the agent to resume an idea.
- **Preconditions**: the incubation bundle and the repository's ordinary execution environment are available.

## 2. Main Success Scenario

1. The agent invokes incubation guidance for the requested product action (`CAP-DLV-idea-incubation`).
2. The agent verifies that the effective development approach permits incubation work (`CAP-DLV-idea-incubation`).
3. The agent recovers current goals, choices and execution evidence from available context and implementation (`CAP-DLV-idea-incubation`).
4. The agent selects the next useful action from the remaining decision or evidence need (`CAP-DLV-idea-incubation`).
5. The agent performs that bounded product action inside the agreed goal and constraints (`CAP-DLV-idea-incubation`).
6. The agent verifies the retained result against intended usage and applicable project checks (`CAP-DLV-idea-incubation`).
7. The agent updates current resume facts and reports observed outcomes, limitations and the next action (`CAP-DLV-idea-incubation`).

## 3. Extensions

- **2a.** SDD approach: the agent stops product work and explains the shared configuration action; the use case ends without changing approach.
- **2b.** Unreadable policy: inspection reports its actual error, including `DEVELOPMENT_CONFIG_INVALID` for an invalid approach; the agent reports the configuration action and the use case ends.
- **3a.** Missing or stale context: the agent recovers current facts from source/run instructions and missing product answers without reconstructing discarded history; resumes at step 4.
- **4a.** Missing product decision: the agent asks only the missing next-action question with its supported recommendation; awaits the product owner's decision, then resumes at step 4.
- **5a.** Goal or constraint change: the agent obtains the product owner's direction before dependent work; resumes at step 4 with the settled direction or ends while that decision is pending.
- **5b.** Optional support: the agent delegates a separable question or usage scope with explicit boundaries, verifies the returned evidence and folds it into current choices; resumes at step 6.
- **5c.** Failed or out-of-scope role result: the agent reports actual partial state and rejects that return as completion evidence; resumes at step 4 without discarding another actor's work.
- **6a.** Failed retained behavior: the agent repairs the implementation within the agreed goal and repeats affected verification; resumes at step 6.
- **6b.** Missing verification evidence: the agent reports the check as unverified and records the gap/next action without claiming successful retained behavior; proceeds to step 7 with that limitation.
- **7a.** Explicit SDD adoption request: the agent explains preparing SDD assets while incubation remains active and routes to the separately available baseline procedure; this use case ends without activating SDD.

## 4. Postconditions

- **Success guarantee**: the bounded action has an observed outcome, relevant current facts and execution instructions are retained, and limitations or the next action are explicit.
- **Minimal guarantee**: no implicit approach switch, invented product decision or skipped-as-passed check is claimed; unrelated edits and existing SDD history are preserved.

## 5. Acceptance Criteria (Given / When / Then)

Rules: approach-gated entry; adaptive next action; bounded evidence; goal-bound iteration; optional role boundaries;
truthful verification; mutable coordinator-owned resume facts; voluntary adoption.

### Scenario 1: Advance a representative flow

- **Covers**: main success scenario
- **Given**: a partial product goal, known local-use constraints and effective incubation.
- **When**: the agent advances a representative implementation action.
- **Then**: the flow is actually exercised, current context records source-specific evidence and no per-change SDD Unit is created.

### Scenario 2: Stop under SDD or invalid policy

- **Covers**: 2a, 2b
- **Given**: effective SDD or an invalid shared approach.
- **When**: incubation entry inspects policy.
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
- **Given**: a separable usage-check scope and an optional role.
- **When**: the role returns evidence or fails its boundary.
- **Then**: the coordinator verifies actual results before fold-back and does not treat a failed or out-of-scope return as completion or authority.

### Scenario 6: Report verification truthfully

- **Covers**: 6a, 6b
- **Given**: failed intended behavior or an unavailable required check.
- **When**: the agent verifies the action.
- **Then**: it repairs and reruns affected checks where possible, while missing evidence remains an explicit limitation.

### Scenario 7: Keep adoption voluntary

- **Covers**: 7a
- **Given**: an explicit request to adopt SDD after incubation.
- **When**: the agent presents the transition doorway.
- **Then**: package/asset preparation is distinguished from baseline readiness and activation; this use case changes no approach.
