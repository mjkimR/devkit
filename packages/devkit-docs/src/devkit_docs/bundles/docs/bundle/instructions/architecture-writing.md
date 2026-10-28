---
name: architecture-writing
description: Read before writing or editing docs/architecture/. Defines arc42 section placement, C4 diagram scope, constraints with their enforcing checks and quality-attribute scenarios.
---

# Architecture Writing

Architecture documents describe the system's structure and the constraints every change keeps. arc42 sections
number the documents (`ARCH-<section>-<slug>`); C4 levels scope the diagrams.

## Placement

- Put content in its arc42 section. Link decisions (section 9) as ADR IDs instead of restating them; the glossary
  (section 12) is `docs/steering/glossary.md`.
- Draw one diagram per C4 level the reader needs, showing only the elements its text discusses.

## Constraints

- State each constraint as one rule with an RFC 2119 keyword and its boundary: "Models MUST NOT import use cases."
- Name the check that enforces it (its fitness function): `RULE-<slug>`, a test path or a CI step. Write "Review
  only" when no check exists, so the gap stays visible.

## Quality Scenarios

Write each quality requirement as a scenario with a measurable response: source, stimulus, environment, response and
measure. Example: an agent runs `<tool> status` in a repository with 500 open specs; it prints one line per open spec
within 2 seconds.
