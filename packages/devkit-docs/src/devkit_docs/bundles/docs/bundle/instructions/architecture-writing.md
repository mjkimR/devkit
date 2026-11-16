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

## Responsibility boundary

- Keep system structure, system interactions, deployment, architectural constraints, cross-cutting technical concepts,
  quality scenarios and risk in architecture; place a local mechanism in design unless it establishes one of those boundaries.
- State strategy and building-block responsibilities in architecture, and keep alternatives/rationale in decisions
  and local algorithms in design.
- Show system interactions in runtime views while keeping actor goals in use cases and observable guarantees in capabilities.
- Distinguish cross-cutting technical concepts from domain meaning, which supplies a conceptual basis alongside
  structure and contracts without a required authoring sequence.
- Keep topology in deployment views; route operational symptoms/evidence through existing recovery owners to
  normal-state observations without duplicating their procedures or permissions.
- Route local implementation detail to formal DESIGN documents, domain concepts to DOMAIN and operational
  evidence/action-owner composition to OPS; read the respective writing instruction before authoring.
- Read `living-spec-writing.md` when the question crosses documentation roles; route by responsibility rather than
  document length, numeric content or arc42 chapter resemblance.

## Constraints

- State each constraint as one rule with an RFC 2119 keyword and its boundary: "Models MUST NOT import use cases."
- Name the check that enforces it (its fitness function): `RULE-<slug>`, a test path or a CI step. Write "Review
  only" when no check exists, so the gap stays visible.

## Quality Scenarios

Write each quality requirement as a scenario with a measurable response: source, stimulus, environment, response and
measure. Example: an agent runs `<tool> status` in a repository with 500 open specs; it prints one line per open spec
within 2 seconds.
