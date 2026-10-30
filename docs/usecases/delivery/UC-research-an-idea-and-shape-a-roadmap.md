---
id: UC-research-an-idea-and-shape-a-roadmap
title: Research an idea and shape an initial roadmap
summary: "An AI coding agent coordinates an explicitly invoked bounded investigation under either development approach, compares early product or architecture directions and retains one indexed research material with supported findings, a conditional roadmap and resumable unknowns."
area: delivery
primary_actor: AI coding agent
supporting_actors: [Product owner, Optional research and discovery subagents]
status: active
capabilities:
  - CAP-DLV-deep-research
  - CAP-HARN-agent-guidance
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/deep_research/bundle/skills/deep-research/SKILL.md
---

# [UC-research-an-idea-and-shape-a-roadmap] Research an idea and shape an initial roadmap

## 1. Goal

- **Goal**: investigate an early product or architecture decision and retain useful evidence, directions,
  initial documents and a conditional roadmap before development.
- **Scope**: one bounded research action and its retained material.
- **Trigger**: the product owner explicitly invokes the research entry.
- **Preconditions**: the deep-research bundle and ordinary project environment are available.

## 2. Main Success Scenario

1. The agent accepts the explicitly invoked research activity (`CAP-DLV-deep-research`, `CAP-HARN-agent-guidance`).
2. The agent recovers current goals, constraints, decisions and supplied evidence without an approach check (`CAP-DLV-deep-research`).
3. The agent frames the decision, comparison criteria and research bound (`CAP-DLV-deep-research`).
4. The agent allocates needed run/task scratch and commissions useful independent investigations inside assigned authority (`CAP-DLV-deep-research`).
5. The agent validates returned sources, actions and candidate assumptions under common criteria (`CAP-DLV-deep-research`).
6. The agent drafts a supported provisional recommendation and unresolved decisions (`CAP-DLV-deep-research`).
7. The agent retains selected documents, evidence and a conditional roadmap as one indexed material with its status (`CAP-DLV-deep-research`).
8. The agent reports the actual outcome, evidence limits, the material's path and ID, the commit the user directs and the next useful action (`CAP-DLV-deep-research`).

## 3. Extensions

- **2a.** SDD project: the explicit invocation is not development intake, so no Unit or classification starts; after the user commits the material, a later proposal, spec or decision cites it by its ID; continues at step 3.
- **2b.** Adaptive (incubation) project: the agent reads no current-context file; after the user commits the material, the current context links it by its ID; continues at step 3.
- **2c.** The user names an earlier run or a `partial` material of the same investigation: the agent reads it as an input source and updates that material at step 7 instead of creating a new one; continues at step 3.
- **3a.** Consequential user decision is missing: the agent reuses known facts and asks only the missing decision; dependent work waits, then resumes at step 3.
- **4a.** Small question: the agent stays inline or uses one support role; resumes at step 5.
- **4b.** Delegation unavailable: the agent uses a permitted equivalent context/contract or reports missing coverage and continues only independently useful authorized work; resumes at step 5.
- **4c.** Scratch is tracked or not ignored in Git: the agent stops allocation and reports the conflict without editing ignore rules; permitted read-only inquiry may continue at step 5.
- **5a.** Unsupported/out-of-scope return: the agent rejects it as evidence, preserves the actual state and reports the affected coverage; resumes at step 3 for a permitted remedy.
- **5b.** Evidence insufficient or bound exhausted: the agent retains partial evidence and missing questions; proceeds to step 6 with no fabricated winner.
- **5c.** Candidate directions share one premise: the agent reframes a useful independent investigation or explains the constraints leaving one viable candidate; resumes at step 3 or proceeds to step 6.
- **7a.** Retained content depends on scratch-only references: the coordinator retains needed supporting evidence or replaces links with stable sources before finishing; resumes at step 7.
- **7b.** The chosen material ID resolves or its directory exists: the coordinator chooses another slug without overwriting the existing material; resumes at step 7.
- **8a.** User authorizes implementation: later work cites the retained material by its ID as ordinary intake; this research action ends without implementation, a commit or publication.

## 4. Postconditions

- **Success guarantee**: one retained material distinguishes evidence, assumptions, recommendations and actual
  decisions; its roadmap is conditional, its `Status` and open questions let a later run or consumer recover the next
  useful decision, and it is left uncommitted for the user's Git policy.
- **Minimal guarantee**: no approach inspection or change, Unit, commit, user approval, role execution or unavailable
  evidence is claimed; no existing material is overwritten; any boundary failure and affected state remain visible.

## 5. Acceptance Criteria

Rules: explicit invocation; approach neutrality; SDD intake exemption; research authority; optional support; bounded
evidence; role boundaries; provenance; research workspace; selective promotion; initial synthesis; one material per
investigation; collision check; resume; citation; bounded partial result; research completion.

### Scenario 1: Compare an initial idea and retain the result

- **Covers**: main success scenario
- **Given**: an incomplete product goal and supplied sources.
- **When**: the agent completes the bounded investigation.
- **Then**: one indexed material covers supported alternatives, a provisional direction, conditional roadmap and explicit unknowns without claiming implemented behavior, and the report names its path, ID and the commit the user directs.

### Scenario 2: Run under either approach

- **Covers**: 2a, 2b
- **Given**: an SDD project, or an adaptive project with a current-context file.
- **When**: the user invokes the research entry.
- **Then**: no approach check, Unit or classification runs, `.devkit/incubation.md` is neither read nor written, and the retained material is cited or linked later by its ID.

### Scenario 3: Ask only the missing consequential decision

- **Covers**: 3a
- **Given**: known users/constraints and one missing decision that changes the target.
- **When**: research is framed.
- **Then**: known answers are reused and only dependent work waits for that decision.

### Scenario 4: Keep a small question small

- **Covers**: 4a
- **Given**: a narrow question answerable inline.
- **When**: the agent chooses research effort.
- **Then**: no full team, document suite or critic round is imposed.

### Scenario 5: Report absent delegation

- **Covers**: 4b
- **Given**: a requested role is unavailable.
- **When**: the agent selects a permitted equivalent or returns partial coverage.
- **Then**: actual execution and emulated/native limits are explicit, with no fabricated role result.

### Scenario 6: Reject unsupported or out-of-scope evidence

- **Covers**: 5a
- **Given**: a return invents authority or exceeds its boundary.
- **When**: the coordinator inspects actual actions and evidence.
- **Then**: it rejects that return as completion evidence and preserves/reports the affected state.

### Scenario 7: Return a bounded partial result

- **Covers**: 5b
- **Given**: conflicting/unavailable evidence or an exhausted research bound.
- **When**: synthesis completes.
- **Then**: unknowns and the next discriminating check survive, with no unsupported choice or date.

### Scenario 8: Examine candidate independence

- **Covers**: 5c
- **Given**: nominal alternatives differ only in one shared unsupported premise.
- **When**: the coordinator compares them.
- **Then**: it investigates a distinct premise or records why constraints leave one candidate; consensus does not establish correctness.

### Scenario 9: Hand the material to later work

- **Covers**: 8a
- **Given**: a committed research material and a later user request for implementation.
- **When**: the later work starts.
- **Then**: it starts as ordinary intake and cites the material by its ID, without treating research completion as approval, a commit or publication.

### Scenario 10: Keep task scratch ignored and separate

- **Covers**: 4c
- **Given**: task scratch would enter tracked or non-ignored Git content.
- **When**: allocation checks the selected path.
- **Then**: allocation stops without an ignore-rule edit, and the report distinguishes any continued read-only inquiry.

### Scenario 11: Promote useful evidence without scratch dependencies

- **Covers**: 7a
- **Given**: an investigation has intermediate task notes and useful supporting evidence.
- **When**: the coordinator retains the synthesis.
- **Then**: selected results and evidence are preserved with resolving durable references, the whole scratch tree is not copied by default, and scratch is not automatically deleted.

### Scenario 12: Resume a partial investigation

- **Covers**: 2c
- **Given**: a `partial` material the user names as the same investigation.
- **When**: the agent retains the resumed result.
- **Then**: it updates that index in place and a `complete` material is never rewritten.

### Scenario 13: Avoid an existing material ID

- **Covers**: 7b
- **Given**: the chosen slug's material ID already resolves.
- **When**: the coordinator creates the material.
- **Then**: it chooses another slug and the existing material is unchanged.
