---
id: UC-explore-a-design-problem
title: Explore a design problem
summary: "An AI coding agent explores materially different general design mechanisms and presents useful directions with tradeoffs so the developer can choose an approach."
area: delivery
primary_actor: AI coding agent
supporting_actors: [Developer, Optional exploration and evidence subagents]
status: active
capabilities:
  - CAP-DLV-design-exploration
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/design_explore/bundle/skills/design-explore/SKILL.md
---

# [UC-explore-a-design-problem] Explore a design problem

## 1. Goal

- **Goal**: choose a useful design direction with understandable benefits, costs and decision-changing uncertainty.
- **Scope**: one bounded architecture, model, module or workflow design problem.
- **Trigger**: the developer explicitly invokes the exploration entry.
- **Preconditions**: the selected bundle and ordinary consumer environment are available.

## 2. Main Success Scenario

1. The agent recovers the goal, existing design, hard constraints and preferences (`CAP-DLV-design-exploration`).
2. The agent selects useful premises and evidence questions (`CAP-DLV-design-exploration`).
3. The agent explores concrete mechanisms through the selected perspectives (`CAP-DLV-design-exploration`).
4. The agent compares relevant consequences and preserves useful differences (`CAP-DLV-design-exploration`).
5. The agent presents directions, tradeoffs, a justified recommendation and remaining uncertainty in conversation
   (`CAP-DLV-design-exploration`).

## 3. Extensions

- **1a.** A missing fact changes useful directions: the agent asks only for that fact; dependent exploration waits
  and resumes at step 1 after the answer.
- **2a.** The question is small: the agent works inline without roles, research or criticism; resumes at step 4.
- **3a.** Fresh children are unavailable: the agent performs useful inline passes and discloses shared context;
  resumes at step 4 without claiming independent exploration.
- **3b.** Research or a role return is incomplete: the agent identifies inspected support, inference and missing
  coverage; resumes at step 4 using only actual returns.
- **4a.** Criticism can change a consequential choice: the agent uses a bounded pass, permits zero findings and
  normally refines once; resumes at step 4 without a score or consensus quota.
- **5a.** An output destination was explicitly requested: only the coordinator writes the authorized result in
  that destination's existing format; the use case ends with that result.
- **5b.** The requested destination is unavailable or refused: the agent keeps the useful conversation result and
  names the blocked write without another route around the refusal; the use case ends with that limitation.

## 4. Postconditions

- **Success guarantee**: the developer receives useful design directions with distinct mechanisms, tradeoffs and
  uncertainty in conversation or the explicitly requested destination.
- **Minimal guarantee**: missing evidence and shared-context limitations remain explicit; no implementation,
  settings change, commit, approval or publication follows from invocation alone.

## 5. Acceptance Criteria

Rules: preserved goal, local assignments, independent first passes, honest fallback, output authority, optional
support, preserved differences, bounded uncertainty and refused operation (`CAP-DLV-design-exploration`).

### Scenario 1: Explain architecture mechanisms

- **Covers**: main success scenario
- **Given**: a status-sharing problem with ownership and latency constraints.
- **When**: the agent compares relevant coordination mechanisms.
- **Then**: it explains ownership, failure behavior, benefit and adoption cost; database brand changes alone are
  not presented as different architectures, and no product code changes.

### Scenario 2: Recover a consequential constraint

- **Covers**: 1a
- **Given**: one missing constraint changes the useful mechanisms.
- **When**: the agent frames the problem.
- **Then**: it asks for that fact and waits on dependent exploration without requiring a formal design brief.

### Scenario 3: Keep a small question inline

- **Covers**: 2a
- **Given**: a small module ownership question.
- **When**: the agent selects useful work.
- **Then**: it can return one useful direction inline without a cast, option quota or benefit experiment.

### Scenario 4: Disclose shared-context passes

- **Covers**: 3a
- **Given**: the host cannot spawn fresh contexts.
- **When**: the agent explores selected premises inline.
- **Then**: it discloses that the passes were not independent contexts and fabricates no role returns.

### Scenario 5: Retain evidence limits

- **Covers**: 3b
- **Given**: an external precedent cannot be inspected or a role fails to return.
- **When**: the agent synthesizes actual evidence.
- **Then**: the result names the evidence gap rather than treating absence as agreement.

### Scenario 6: Permit zero critique findings

- **Covers**: 4a
- **Given**: a plausible unusual mechanism and no supported consequential defect.
- **When**: the critic checks it against the constraints.
- **Then**: zero findings is valid and the useful mechanism survives without forced consensus.

### Scenario 7: Honor a requested destination

- **Covers**: 5a
- **Given**: the developer explicitly requests an existing design note as the destination.
- **When**: the coordinator writes the result under project rules.
- **Then**: only the authorized note changes; no implementation or delivery approval is created.

### Scenario 8: Preserve a refused result

- **Covers**: 5b
- **Given**: the requested destination write is refused.
- **When**: the coordinator reaches that action.
- **Then**: it returns the useful directions in conversation and identifies the blocked write without bypass.
