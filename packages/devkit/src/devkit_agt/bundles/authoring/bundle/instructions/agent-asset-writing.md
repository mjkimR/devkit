---
name: agent-asset-writing
description: Read before writing or editing a skill, playbook, instruction or subagent. Defines directive writing, conditional loading, role placement, bounded delegation and bundle self-containment.
---

# Agent Asset Writing

An agent loads a skill, playbook, instruction or subagent role to act on it. Write only what this repository adds to what the agent
already knows, and cut every line that does not change its next action.

## Directives

- Write one imperative directive per line or list item, condition first: "If `plan.md` is missing, create it."
- Pair a prohibition with its alternative when one exists: "Edit the bundle source, not the projected copy."
- Give a reason in one clause only when it changes how the agent applies the directive.
- Write no hedges ("likely", "might", "consider") and no emphasis ("CRITICAL", capitals, bold); emphatic wording
  makes models over-apply a directive.
- Use one term per concept; a synonym reads as a different concept.

## Degrees of Freedom

| Step | Write |
| --- | --- |
| Fragile, order-sensitive or destructive | The exact command or script, no alternatives |
| A preferred pattern with valid variations | A template or parameterized command |
| Context-dependent judgment | Criteria and heuristics |

- Offer one default and the condition for its exception, not a list of equal options.
- Delegate an ordering that must hold to a gate, check or script, and name the command that enforces it.
- Name exact identifiers: commands with flags, codes, paths, tool names qualified by their server.
- Show one concrete example per pattern.

## Procedures

- Number the steps. Close a quality-critical step with a loop: run the validator, fix what it reports, repeat until
  it passes.
- End with completion criteria the agent can check: a command and its expected result, a file state or an output
  line.

## Structure

- Keep in the main file what every run needs: purpose and trigger, constraints, procedure, completion criteria.
- Move what only some runs need into references one level deep, each linked with its read condition: "Read
  `references/recovery.md` when the sync fails." Never send the agent to read every reference up front.
- Say whether the agent runs a script or reads it.
- Leave out what another asset owns (link the owner), what a command's output already tells the agent, and
  time-relative facts ("recently", "the new API").

## Role Placement

- For a role used only within one skill, keep its instructions in the skill's `roles/<role>.md` by default, so its
  metadata stays out of the global subagent list.
- Register a subagent when it needs independent selection outside that skill or role-specific host settings that
  a general subagent invocation cannot supply, such as model, tool or sandbox settings.
- Keep role procedures and return requirements separate from host execution settings; Markdown instructions do
  not enforce tool permissions or sandbox boundaries.
- In the skill, route each delegated task to one role file and tell a general subagent to read that file first;
  pass its absolute installed path without loading every role body into the coordinator.
- Supply the child with its goal, relevant sources, read/write boundaries, permitted actions, stop condition and
  expected return; make its assigned role file readable within those boundaries.
- Where the host supports it, spawn with a fresh context without parent conversation inheritance; otherwise
  report that limitation and pass only the task's required information.
- When required delegation or permissions are unavailable, report missing coverage; never describe a prompt as
  native enforcement.

Example assignment prefix: `Read /absolute/installed/skill/roles/critic.md first, then review the supplied draft
within the assigned read boundaries and return the findings in that role's format.`

## Self-Containment

A bundle ships to repositories that have none of the authoring repository's documents. Link only the bundle's own
assets, and write a rule with its reason instead of citing the authoring repository's documents or paths.

- Cite none of the authoring repository's document IDs, of any kind (`ADR-`, `CAP-`, `UC-`, `UX-`, `ARCH-`, `SPEC-`,
  `PROP-`, `MS-`, `MAT-`, `FB-` and the others), even when the rule comes from one.
- Cite a document ID only when a bundle seeds that document into the consuming project.
- Name consumer documents and example IDs only as placeholders or examples that name no real document
  (`docs/decisions/`, `ADR-example`, `CAP-<AREA>-<slug>`).

## Completion

- `rg -n '\b(ADR|PADR|CAP|UC|UX|ARCH|SPEC|PROP|MS|MAT|FB)-[A-Za-z0-9]' <bundle directory>` reports only
  placeholders, examples and the IDs of seeded documents.
- `uv run devkit rules check --phase hygiene <asset>` reports no `RULE-agent-asset-wording` warning.
- Every line of the asset meets the directives above.
