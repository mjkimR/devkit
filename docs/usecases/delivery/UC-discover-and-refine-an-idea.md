---
id: UC-discover-and-refine-an-idea
title: Discover and refine an idea
summary: "An AI coding agent turns a developer's half-formed idea into concrete proposals and a next decision with limited interviewing, optional independent exploration and uncertainty-driven routing."
area: delivery
primary_actor: AI coding agent
supporting_actors: [Developer, Optional discovery subagents]
status: active
created_at: 2026-11-13
capabilities:
  - CAP-DLV-idea-discovery
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/deep_research/bundle/skills/discovery/SKILL.md
---

# [UC-discover-and-refine-an-idea] Discover and refine an idea

## 1. Goal

- **Goal**: help the developer judge concrete proposals and choose a useful next step for a half-formed idea.
- **Scope**: one bounded discovery conversation, including a supported rejection.
- **Trigger**: the developer explicitly invokes discovery.
- **Preconditions**: the selected bundle and ordinary consumer environment are available.

## 2. Main Success Scenario

1. The agent reads supplied context and recovers the desired change, use scene, constraints and session outcome
   (`CAP-DLV-idea-discovery`).
2. The agent frames a bounded exploration, preserving open preferences as assumptions or alternative premises
   (`CAP-DLV-idea-discovery`).
3. The agent develops concrete proposals and inspects decision-changing evidence, using useful independent
   perspectives (`CAP-DLV-idea-discovery`).
4. The agent pressure-tests consequential premises after candidate development (`CAP-DLV-idea-discovery`).
5. The agent compares actual findings and routes remaining uncertainty (`CAP-DLV-idea-discovery`).
6. The agent returns concrete proposals, a justified recommendation, the outcome and the next decision in
   conversation (`CAP-DLV-idea-discovery`).

## 3. Extensions

- **1a.** An unanswered owner-only choice changes the first proposals: the agent asks the focused question with
  its consequence and waits for dependent work; resumes at step 1 after the answer.
- **3a.** Independent delegation or evidence is unavailable: the agent discloses missing coverage and performs
  useful inline work without claiming independent execution; resumes at step 4.
- **5a.** A factual gap changes the recommendation: the agent names the question and discriminating result and
  investigates within the bound; resumes at step 3 or returns validation-needed when the bound is reached.
- **5b.** An experiential gap needs execution: the agent shows an inline example or proposes a bounded experiment;
  the use case ends validation-needed without running it on discovery authority.
- **5c.** A central premise fails: the agent recommends reframing within scope, holding or rejecting the idea;
  the use case ends with the failure evidence and surviving uncertainty.
- **6a.** The developer requested retention: the coordinator writes the authorized result under project rules;
  the use case ends with its path, identity and coverage status.
- ***a.** Access or a destination write is refused: the agent stops that resource and reports the blocked
  coverage without bypass; resumes with unrelated permitted work or ends with the useful partial result.

## 4. Postconditions

- **Success guarantee**: the developer receives concrete proposals or a supported hold/rejection with evidence
  limits, separated decisions/assumptions and a next route.
- **Minimal guarantee**: missing support is explicit; no implementation, delivery Unit, settings change, commit
  or publication follows from discovery alone.

## 5. Acceptance Criteria

Rules: minimum interview, bounded exploration, honest fallback, uncertainty routing, execution authority,
discovery outcome, requested retention and refused access (`CAP-DLV-idea-discovery`).

### Scenario 1: Turn reading frustration into proposals

- **Covers**: main success scenario
- **Given**: a developer describes losing useful reading, their current routine and a low-maintenance constraint.
- **When**: discovery has enough context for a first wave.
- **Then**: it presents concrete usage examples, costs and assumptions without first asking for a technology stack;
  no retained file or delivery Unit is created.

### Scenario 2: Ask a consequential owner question

- **Covers**: 1a
- **Given**: whether the idea serves the developer or a paid customer changes useful proposals.
- **When**: context does not answer that choice.
- **Then**: the agent asks with the concrete consequence and invents no confirmed audience.

### Scenario 3: Disclose missing independence

- **Covers**: 3a
- **Given**: the host cannot run fresh subagents.
- **When**: the agent develops proposals inline.
- **Then**: it identifies missing independent coverage rather than inventing role returns.

### Scenario 4: Investigate a factual discriminator

- **Covers**: 5a
- **Given**: a required existing tool capability is unverified.
- **When**: that capability determines whether a proposal is feasible.
- **Then**: the agent researches that question within the bound or reports validation-needed with the gap.

### Scenario 5: Propose an experiment without running it

- **Covers**: 5b
- **Given**: judging a workflow requires trying it on private documents.
- **When**: no execution or document-edit authority was granted.
- **Then**: the agent returns the experiment's question and boundary with no private-document changes.

### Scenario 6: Reject a failed premise

- **Covers**: 5c
- **Given**: inspected evidence undermines the central expected benefit.
- **When**: further inquiry would not change the next decision.
- **Then**: rejected or held is a valid outcome without a forced implementation plan.

### Scenario 7: Retain only on request

- **Covers**: 6a
- **Given**: the developer requests a durable discovery material.
- **When**: the coordinator retains its useful synthesis.
- **Then**: it reports a collision-free material identity and complete/partial coverage status separately from
  the discovery outcome, leaving the result uncommitted.

### Scenario 8: Preserve denied access

- **Covers**: *a
- **Given**: a needed source or destination is refused.
- **When**: the agent reaches the refused operation.
- **Then**: it reports the limitation and attempts no alternate access route.
