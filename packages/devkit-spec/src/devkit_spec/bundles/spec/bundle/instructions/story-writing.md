---
name: story-writing
description: Read before writing or editing a user story (docs/stories/). Defines the narrative, Example Mapping from rules to Given/When/Then scenarios, and the background a story keeps.
---

# Story Writing

A story states what one actor achieves and how the outcome is accepted. The capabilities it links through
`capabilities:` hold the system rules it relies on. Start from the `story` template.

## Narrative

- **As a**: the narrowest actor that fits (operator, AI agent, reviewer), not "user" when a narrower role exists.
- **I want to**: the outcome the actor seeks, not a UI step or an implementation.
- **So that**: the value the outcome gives the actor.

## Scenarios by Example Mapping

1. List the rules the story depends on, one line each.
2. For each rule, choose one example per distinct outcome: the main path, a boundary and a refusal.
3. Write each example as one Given/When/Then scenario: one set of preconditions, one action, observable results
   (an exit code, an output line, a file state).
4. Title each scenario with the rule and the case: "Refuses an unknown bundle".
5. Resolve each open question before its scenario enters the story; until then it belongs to the spec or proposal
   that changes the story.

## Background

- Keep "Background & Context" to the preconditions the scenarios share. Link the spec or ADR that holds the
  motivation by ID.
