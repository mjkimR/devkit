---
name: architecture-writing
description: Read before writing or editing docs/architecture/. Defines arc42 section placement, C4 diagram scope, constraints with their enforcing checks and quality-attribute scenarios.
---

# Architecture Writing

Architecture documents describe the system's structure and the constraints every change keeps. arc42 sections
number the documents (`ARCH-<section>-<slug>`); C4 levels scope the diagrams.

## Placement

- Put content in its arc42 section: goals (1), constraints (2), context (3), solution strategy (4), building blocks
  (5), runtime (6), deployment (7), cross-cutting concepts (8), quality (10), risks (11).
- Link decisions (arc42 section 9) as ADR IDs instead of restating them; the glossary (section 12) is
  `docs/glossary.md`.
- Draw one diagram per C4 level the reader needs (context, containers, components). Show only the elements its text
  discusses.

## Constraints

- State each constraint as one rule with an RFC 2119 keyword and its boundary: "Models MUST NOT import use cases."
- Name the check that enforces it (its fitness function): `RULE-<slug>`, a test path or a CI step. Write "review
  only" when no check exists, so the gap stays visible.

## Quality Scenarios

Write each quality requirement as a scenario whose response is measurable:

| Part | Content | Illustrative example |
| --- | --- | --- |
| Source | Who or what causes the stimulus | An agent |
| Stimulus | The event | Runs `<tool> status` |
| Environment | The conditions | A repository with 500 open specs |
| Response | What the system does | Prints one line per open spec |
| Measure | The bound that verifies it | Within 2 seconds |
