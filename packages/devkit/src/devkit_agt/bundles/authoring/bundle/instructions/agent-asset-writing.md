---
name: agent-asset-writing
description: Read before writing or editing a skill, playbook or instruction an agent executes. Defines directive sentences, degrees of freedom, defaults, feedback loops, completion criteria, emphasis, conditional references and bundle self-containment.
---

# Agent Asset Writing

An agent loads a skill, playbook or instruction to act on it. Every line either changes what the agent does next or
is removed. Assume the agent already knows the language, the tools and general practice; write only what this
repository adds.

## Directives

- Write imperative directives, one per line or list item: "Run `devkit sync` after editing a bundle source."
- Put the condition first: "If `plan.md` is missing, create it with ...".
- Pair a prohibition with its alternative when one exists: "Edit the bundle source, not the projected copy." A
  prohibition whose alternative is to do nothing stands alone.
- Give a reason in one clause when it changes how the agent applies the directive: "..., because the file is
  shared in the PR." Link background and history by ID or path instead of retelling them, within the limits of
  Self-Containment.
- Write without hedges ("likely", "might", "consider"); state the condition under which the directive applies.
- Use plain directives instead of "CRITICAL", "ALWAYS", "NEVER" in capitals or bold. Emphatic wording makes current
  models over-apply a directive; its condition and reason give it the right force.
- Use one term per concept throughout the asset; a synonym reads as a different concept.

## Degrees of Freedom

Match the precision of a step to how fragile it is:

| Step | Write | Example |
| --- | --- | --- |
| Fragile, order-sensitive or destructive | The exact command or script, no alternatives | `python3 scripts/migrate.py --verify` |
| A preferred pattern with valid variations | A template or parameterized command | A report skeleton the agent fills |
| Context-dependent judgment | Criteria and heuristics | "Group findings by severity" |

- Offer one default and the condition for its exception instead of a list of equal options: "Use `rg`; for a
  binary file use `git grep -a`."
- Delegate an ordering that must hold to a gate, check or script; a sentence is skipped under pressure, a gate is
  not. Tell the agent which command enforces it.

## Procedures and Completion

- Number the steps of a procedure; for a long one, give a checklist the agent copies and ticks.
- Close a quality-critical step with a feedback loop: run the validator, fix what it reports, run it again, and
  continue only when it passes.
- End the asset with completion criteria the agent can check: a command and its expected result, a file state or
  an output line.
- Name exact identifiers: commands with flags, codes, paths, tool names qualified by their server.
- Show one concrete input/output example per pattern; move long or rare examples to a reference.

## Structure

- Keep what every run needs in the main file: purpose and trigger, constraints, procedure, completion criteria.
- Move what only some runs need into references one level deep, each linked with its read condition: "Read
  `references/recovery.md` when the sync fails." Never send the agent to read every reference up front.
- Say whether the agent runs a script or reads it. A script prints only the slice the agent needs.
- State no time-relative facts ("recently", "the new API"); describe the current state.

## Self-Containment

A bundle is the unit a package ships to other repositories, which have none of the authoring repository's
documents. Each bundle is self-contained: its assets may reference each other, but nothing outside the bundle.

- Link freely to the bundle's own assets: its skills and their references, instructions, playbooks, templates,
  rules and workflows.
- Write the rule and its one-clause reason in the asset instead of citing the authoring repository's ADR, capability,
  story, spec or path: "Do not write the OK to a file." not "... (`ADR-...`)".
- Refer to the consumer repository's own documents only through a placeholder (`docs/decisions/`, `ADR-<slug>`).
- Name example IDs as obvious placeholders (`ADR-example`, `CAP-<AREA>-<slug>`), never as real IDs of the authoring
  repository.
- Before committing a bundle change, search the bundle for document IDs:
  `rg -n '\b(ADR|CAP|US|ARCH|SPEC|MS)-[a-z]' <bundle directory>`; each hit is a placeholder or removed.

## Completion

- Every line changes the agent's next action or is a needed condition, reason or example.
- Every prohibition has its alternative or needs none; no hedged directive, no emphatic capitals outside defined
  keywords.
- Every required ordering names its enforcing command; the asset ends with checkable completion criteria.
- Every reference is linked with a read condition, one level deep.
- The bundle cites nothing outside itself except placeholders for the consumer repository's documents.
