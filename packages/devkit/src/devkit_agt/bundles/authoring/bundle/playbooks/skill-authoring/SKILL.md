---
name: skill-authoring
description: Create an agent skill or playbook with a router structure, restructure one that grew too large (RULE-skill-document-size), and decide when it needs a helper script.
---

# Skill authoring and restructuring

Use when you create or substantially edit a skill or playbook, or when `RULE-skill-document-size` reports one.
Write it by the `agent-asset-writing` instruction. Read [script support](references/scripts.md) when a step is
repetitive and deterministic, or must filter repository state down to the slice the agent needs. For a bundle
source, run `devkit sync` after editing.

## Constraints

- Keep every instruction that applies on every run in `SKILL.md`, including safety, scope and boundary constraints.
- Do not shrink a file by joining lines, dropping completion criteria or deleting examples the procedure depends on.
- Restructure as the task itself or in a hygiene session, not inside unrelated feature work.

## Step 1: Create a skill as a router

- Make `description` say what the skill does and when to use it, in the words a user or agent would type; it
  decides whether the skill triggers.
- Put each situation or procedure that only some runs need in its own `references/<situation>.md`.

## Step 2: Restructure a large skill

Aim for about 75-80% of the effective `max_bytes`; never split an inseparable procedure to get there.

1. Move conditional content first: recovery procedures, tool- or host-specific instructions, one stage's detailed
   schema, rare long examples.
2. Leave `SKILL.md` as a router: purpose and trigger, shared constraints, task branches, reference paths.
3. Remove repeated explanation, long background and overlapping examples.
4. Apply the same steps to a large reference. Avoid many tiny files and references that send the agent to another
   reference.

If a file must stay large (one procedure always read whole, a quoted external protocol), record the override that
`devkit rules explain RULE-skill-document-size` shows.

## Completion conditions

- Every link from `SKILL.md` resolves, and every reference is linked with a read condition.
- `uv run devkit rules check --phase hygiene` reports no `RULE-skill-document-size` warning for the edited files, or
  the file has a commented override.
