---
id: UC-research-an-idea-and-shape-a-roadmap
title: Research an idea and shape an initial roadmap
summary: "An AI coding agent coordinates an explicitly selected bounded investigation, compares early product directions and retains supported initial documents, a conditional roadmap and resumable unknowns."
area: delivery
primary_actor: AI coding agent
supporting_actors: [Product owner, Optional research and discovery subagents]
status: active
capabilities:
  - CAP-DLV-idea-incubation
  - CAP-HARN-agent-guidance
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/deep_research/bundle/skills/deep-research/SKILL.md
---

# [UC-research-an-idea-and-shape-a-roadmap] Research an idea and shape an initial roadmap

## 1. Goal

- **Goal**: investigate an early product or architecture decision and retain useful evidence, directions,
  initial documents and a conditional roadmap before development.
- **Scope**: one bounded research action and its current/resume facts.
- **Trigger**: the product owner explicitly selects the research entry.
- **Preconditions**: the incubation bundle and ordinary project environment are available.

## 2. Main Success Scenario

1. The agent accepts the explicitly selected research activity (`CAP-DLV-idea-incubation`, `CAP-HARN-agent-guidance`).
2. The agent checks approach and recovers current goals, constraints, decisions and supplied evidence (`CAP-DLV-idea-incubation`).
3. The agent frames the decision, comparison criteria and research bound (`CAP-DLV-idea-incubation`).
4. The agent allocates needed run/task scratch and commissions useful independent investigations inside assigned authority (`CAP-DLV-idea-incubation`).
5. The agent validates returned sources, actions and candidate assumptions under common criteria (`CAP-DLV-idea-incubation`).
6. The agent drafts a supported provisional recommendation and unresolved decisions (`CAP-DLV-idea-incubation`).
7. The agent promotes selected documents and evidence, a conditional roadmap and current resume facts (`CAP-DLV-idea-incubation`).
8. The agent reports the actual outcome, evidence limits, retained paths and next useful action (`CAP-DLV-idea-incubation`).

## 3. Extensions

- **2a.** SDD approach: the agent stops product actions and reports the shared configuration action; the use case ends without switching approach.
- **2b.** Invalid/unreadable policy: the agent reports the actual policy error and next configuration action; the use case ends without product writes.
- **3a.** Consequential user decision is missing: the agent reuses known facts and asks only the missing decision; dependent work waits, then resumes at step 3.
- **4a.** Small question: the agent stays inline or uses one support role; resumes at step 5.
- **4b.** Delegation unavailable: the agent uses a permitted equivalent context/contract or reports missing coverage and continues only independently useful authorized work; resumes at step 5.
- **4c.** Scratch is tracked or not ignored in Git: the agent stops allocation and reports the conflict without editing ignore rules; permitted read-only inquiry may continue at step 5.
- **5a.** Unsupported/out-of-scope return: the agent rejects it as evidence, preserves the actual state and reports the affected coverage; resumes at step 3 for a permitted remedy.
- **5b.** Evidence insufficient or bound exhausted: the agent retains partial evidence and missing questions; proceeds to step 6 with no fabricated winner.
- **5c.** Candidate directions share one premise: the agent reframes a useful independent investigation or explains the constraints leaving one viable candidate; resumes at step 3 or proceeds to step 6.
- **8a.** User authorizes implementation: the agent passes retained facts to the authorized product action; this research action ends without automatic SDD adoption or publication.

- **7a.** Retained content depends on scratch-only references: the coordinator retains needed supporting evidence or replaces links with stable sources before finishing; resumes at step 7.

## 4. Postconditions

- **Success guarantee**: retained notes/current facts distinguish evidence, assumptions, recommendations and actual
  decisions; the roadmap is conditional and a later context can recover the next useful decision.
- **Minimal guarantee**: no implicit approach change, user approval, role execution or unavailable evidence is
  claimed; any boundary failure and affected state remain visible.

## 5. Acceptance Criteria

Rules: explicit research entry; approach inspection; adaptive clarification; optional support; bounded evidence;
role boundaries; provenance; research workspace; selective promotion; initial synthesis; useful alternatives; bounded partial result; research completion.

### Scenario 1: Compare an initial idea and retain the result

- **Covers**: main success scenario
- **Given**: an incomplete product goal, permitted incubation and supplied sources.
- **When**: the agent completes the bounded investigation.
- **Then**: retained notes cover supported alternatives, a provisional direction, conditional roadmap and explicit unknowns without claiming implemented behavior.

### Scenario 2: Refuse incompatible or invalid policy

- **Covers**: 2a, 2b
- **Given**: effective SDD or an invalid approach.
- **When**: the research entry checks policy.
- **Then**: the actual configuration action/error is reported and product files remain unchanged.

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

### Scenario 9: Hand facts to an authorized next action

- **Covers**: 8a
- **Given**: research output and subsequent user implementation authority.
- **When**: the next product action begins.
- **Then**: it consumes the retained current facts without treating research completion as SDD activation or publication approval.

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
