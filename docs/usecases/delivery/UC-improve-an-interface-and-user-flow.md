---
id: UC-improve-an-interface-and-user-flow
title: Improve an interface and user flow
summary: "An AI coding agent uses an explicitly invoked UI/UX skill to improve a supplied user task, apply requested design changes through the existing project workflow and report actual verification and limits."
area: delivery
primary_actor: AI coding agent
supporting_actors: [Product owner, Optional design and research subagents]
status: active
capabilities:
  - CAP-DLV-uiux-improvement
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/uiux_improve/bundle/skills/uiux-improve/SKILL.md
---

# [UC-improve-an-interface-and-user-flow] Improve an interface and user flow

## 1. Goal

- **Goal**: improve the supplied interface or flow so that it serves the intended user task more clearly and usefully.
- **Scope**: one bounded UI/UX improvement request.
- **Trigger**: the product owner explicitly invokes the improvement entry.
- **Preconditions**: the selected bundle and ordinary project environment are available.

## 2. Main Success Scenario

1. The agent recovers the target, intended outcome, relevant artifacts and constraints (`CAP-DLV-uiux-improvement`).
2. The agent inspects the representative task path and affected interface states (`CAP-DLV-uiux-improvement`).
3. The agent develops useful design perspectives for the requested improvement (`CAP-DLV-uiux-improvement`).
4. The agent synthesizes a coherent direction and its relevant tradeoffs (`CAP-DLV-uiux-improvement`).
5. The agent applies requested changes through the consumer's existing delivery workflow (`CAP-DLV-uiux-improvement`).
6. The agent checks the changed interface and representative interactions (`CAP-DLV-uiux-improvement`).
7. The agent reports the actual improvement, verification and material limits (`CAP-DLV-uiux-improvement`).

## 3. Extensions

- **1a.** A decision-changing artifact or constraint is missing: the agent reuses known context and asks only for
  that missing input; dependent work waits and resumes at step 1.
- **2a.** The running interface cannot be inspected: the agent uses available screenshot, code or text evidence and
  names its coverage; continues at step 3 without claiming actual interaction verification.
- **3a.** A small request needs no team or research: the agent works inline; resumes at step 4.
- **3b.** Fresh children are unavailable: the agent uses useful inline passes and discloses their shared context;
  resumes at step 4 without fabricated role findings.
- **4a.** A product or scope decision exceeds existing authority: the agent presents the concrete choice and preserves
  independent useful work; dependent work waits and resumes at step 4 after the user's decision.
- **5a.** Review-only request: the agent returns findings without product edits; the use case ends with the requested review.
- **5b.** A workflow approval or tool is missing: the agent preserves useful partial work and names the blocker;
  the use case ends pending that requirement.
- **6a.** A check exposes a defect: the agent fixes it within scope and repeats the affected check; resumes at step 6.

## 4. Postconditions

- **Success guarantee**: requested changes and actual verification are reported; narrower review requests return
  findings with no product edits, and the result respects the requested destination and project ownership.
- **Minimal guarantee**: unavailable work and checks remain explicit; no native isolation, workflow approval,
  publication or real-user quality result is invented.

## 5. Acceptance Criteria

Rules: explicit invocation, consumer authority, goal-driven improvement, narrower request, optional perspectives,
role packet, independent context, host limits, verification and qualified completion.

### Scenario 1: Carry a flow and visual improvement through delivery

- **Covers**: main success scenario, 6a
- **Given**: a supplied interface, user goal and authorized improvement scope.
- **When**: the agent applies the selected direction through the project workflow.
- **Then**: the changed interface and representative task checks are reported, with relevant defects fixed and rechecked.

### Scenario 2: Ask only for a consequential missing input

- **Covers**: 1a, 4a
- **Given**: known facts and one missing input or product choice that changes the authorized work.
- **When**: the agent reaches that choice.
- **Then**: it presents the concrete gap, preserves independent useful work and waits only on dependent actions.

### Scenario 3: Qualify screenshot-only coverage

- **Covers**: 2a
- **Given**: screenshots or code but no running UI tools.
- **When**: the agent assesses or changes the interface.
- **Then**: the result names the evidence and unverified interaction coverage without claiming actual usage checks.

### Scenario 4: Keep optional perspectives proportionate

- **Covers**: 3a, 3b
- **Given**: a narrow request or unavailable fresh children.
- **When**: the agent chooses useful design passes.
- **Then**: it can finish inline, describes shared-context limits and imposes no fixed cast, score or comparison program.

### Scenario 5: Honor a review-only request

- **Covers**: 5a
- **Given**: an explicit request for findings only.
- **When**: the agent reviews the supplied interface.
- **Then**: it returns supported findings, possibly zero, with no product source edits.

### Scenario 6: Preserve blocked improvement work

- **Covers**: 5b
- **Given**: a concrete missing approval, artifact or tool prevents completion.
- **When**: the agent reaches the dependent action.
- **Then**: it retains useful partial work and names that blocker without treating requested implementation as complete.
