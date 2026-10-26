---
name: usecase-writing
description: Read before writing or editing a use case (docs/usecases/). Defines the goal, the main success scenario, extensions keyed to its steps, postconditions and Example Mapping to Given/When/Then scenarios.
---

# Use Case Writing

A use case states how one primary actor reaches one goal through the system, every way it can branch or fail on the
way, and how each outcome is accepted. The capabilities it links through `capabilities:` own the contracts its steps
rely on. Start from the `usecase` template.

## Goal

- One use case, one goal of one primary actor, at the level of a task the actor completes in one sitting ("integrate
  a verified branch"). A step of that task stays a step; a journey of several such goals becomes several use cases.
- `primary_actor` is the narrowest actor that fits (operator, AI coding agent, reviewer), not "user" when a narrower
  role exists. `supporting_actors` lists the actors the system calls on: subagents, a human approver, a remote host.
- **Goal**: the outcome the actor seeks and the value it gives, not a UI step or an implementation.
- **Preconditions**: only state the use case relies on without checking it; a condition the system checks is an
  extension.

## Main Success Scenario

- Three to nine numbered steps from the trigger to the goal, in the order they happen, with no branches.
- Each step is one action of an actor or one response of the system, written as its intent: "The agent requests the
  next stage", not the command line or its flags.
- Cite the capability that owns a step's contract by ID. Command syntax, exit codes, output formats and field lists
  stay in the capability; restate none of them here.
- When the project has UX documents, a step may cite the UX ID of the screen it happens on, next to its capability
  citations; a system step cites the screen its response appears on. Only a step that truly happens off screen (a
  mail sent, a background job) cites none. The screen holds the interface detail; the step stays an intent
  (`ux-writing`).

## Extensions

- For each step, list the conditions under which it goes differently: a refusal, a failure, an alternative path.
  Key each to its step (`3a`, `3b`; `*a` for a condition at any step).
- Write each as the condition, the handling and the end: "the system refuses with `CODE`; the use case ends" or
  "...; resumes at step 4". Name the stable code an agent acts on; the code's full contract stays in the capability.
- Leave out conditions that change nothing the actor observes.

## Postconditions

- **Success guarantee**: the state after the main success scenario and after every extension that reaches the goal.
- **Minimal guarantee**: what the system keeps true when the use case fails: nothing is half-written, a refusal leaves
  the repository unchanged, the actor receives a directive.

## Acceptance Criteria by Example Mapping

1. List the rules the use case depends on, one line each, from the linked capabilities.
2. For each rule, choose one example per distinct outcome: the main path, a boundary and a refusal.
3. Write each example as one Given/When/Then scenario: one set of preconditions, one action, observable results
   (an exit code, an output line, a file state).
4. Name what the scenario covers on its `Covers` line: the main success scenario or an extension key. Every extension
   that changes the outcome has at least one scenario.
5. Title each scenario with the rule and the case: "Refuses an unknown bundle".
6. Resolve each open question before its scenario enters the use case; until then it belongs to the spec or proposal
   that changes the use case.

## Use Cases and Feature Specs

A feature spec (`spec.md`) states its intent as user stories; they are the request, not the contract. When the spec
completes, `spec-sync` folds the delivered behavior into the use cases it changes: new steps, extensions,
postconditions and scenarios.
