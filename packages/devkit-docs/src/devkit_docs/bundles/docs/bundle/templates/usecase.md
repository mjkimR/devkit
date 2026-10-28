---
id: UC-<slug>
title: Use Case Title (the goal as a verb phrase, e.g., Integrate a Verified Branch)
summary: "One or two English sentences: which actor achieves what goal through this use case"   # required, English; quote it, it may contain ": "
area: <area>              # Must match parent directory docs/usecases/<area>/
primary_actor: <!-- the actor whose goal this is: AI coding agent | Operator | Reviewer, etc. -->
supporting_actors: []     # actors the system calls on during the use case: subagents, a human approver, external systems
status: proposed          # proposed | active | completed | deprecated
capabilities:
  - CAP-<AREA>-<slug>
---

# [UC-<slug>] Use Case Title

<!-- File path is docs/usecases/<area>/UC-<slug>.md and id matches file name. No sequence numbers. -->

## 1. Goal

- **Goal**: <!-- the outcome the primary actor seeks -->, so that <!-- the value it gives the actor -->
- **Scope**: <!-- the system under discussion: a command group, a workflow, a package -->
- **Trigger**: <!-- the event that starts the use case -->
- **Preconditions**: <!-- the state that holds before the trigger; the use case does not check it again -->

---

## 2. Main Success Scenario
<!-- Numbered steps, one actor action or system response each; cite the capability that owns a step's contract (usecase-writing) -->

1. <!-- Actor ... -->
2. <!-- The system ... (`CAP-<AREA>-<slug>`) -->

---

## 3. Extensions
<!-- Keyed to the step they branch from (`2a`, `2b`; `*a` for any step): the condition, the handling with its stable code, and where the use case resumes or ends -->

- **2a.** <!-- Condition -->: <!-- handling, e.g., the system refuses with `CODE` -->; <!-- resumes at step N | the use case ends -->.

---

## 4. Postconditions

- **Success guarantee**: <!-- the state after the main success scenario or a successful extension -->
- **Minimal guarantee**: <!-- what holds even when the use case ends in failure -->

---

## 5. Acceptance Criteria (Given / When / Then)
<!-- Derive scenarios by Example Mapping (usecase-writing): one per distinct outcome of the main scenario and each extension -->

### Scenario 1: [Main Success Scenario Name]
- **Covers**: main success scenario
- **Given**: <!-- Precondition -->
- **When**: <!-- Action occurs -->
- **Then**: <!-- Verification result -->

### Scenario 2: [Extension Scenario Name]
- **Covers**: <!-- extension key, e.g., 2a -->
- **Given**: <!-- Precondition -->
- **When**: <!-- Action occurs -->
- **Then**: <!-- Verification result -->
