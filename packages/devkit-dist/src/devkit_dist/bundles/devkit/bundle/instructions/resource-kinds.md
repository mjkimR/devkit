---
name: resource-kinds
description: Read before choosing the kind of a new asset (rule, gate, skill, subagent, instruction, playbook, workflow, guidance, document or hook).
---

# Choosing an asset kind

Choose the kind from what the content is, not from how often it is needed:

```text
Can a program verify the invariant with certainty?            -> rule      rules/<slug>/
Must it run at a Git hook stage and block a commit?           -> gate      gates/<slug>/
Is it a tool or script directory the agent executes?          -> skill     skills/<slug>/SKILL.md
Is it a delegated persona?                                    -> subagent  subagents/<slug>.md
Is it a recurring multi-stage delivery flow?                  -> workflow  one Markdown definition
Is it a procedure for an occasional task?                     -> playbook  playbooks/<slug>.md
Does every task of the bundle need it, read before anything?  -> AGENTS.md (constitution)
Otherwise (policies, standards, judgment criteria)            -> instruction  instructions/<slug>.md
```

Three kinds sit outside the tree: `document` (read by path; with `seeded = true`
a scaffold the project owns after the first sync), `guidance` (a pointer line in
the root `AGENTS.md` block for a moment no skill marks) and `hook` (a handler
the agent host calls at a native event).

- Write a rule when a check can be decided mechanically, even if a sentence is
  shorter, because a rule costs no context and runs in gates.
- Keep the constitution and guidance to what every task needs, because they are
  read on every context load or every turn.
- Write a `description` that says when to read the asset, because the agent
  decides from the header alone.
- Do not write the bundle-context prerequisite in a skill; sync adds it.
- For a skill only the user should start, declare `invocation = "user"` in
  `bundle.toml`.
- Keep rule ids unique across the installed bundles; a later rule with the same
  id replaces an earlier one.

For a `.md.jinja` source, declare each input under `[variables.<name>]` with a
`type` and, for a local `bundle plan`, a `default`; reference it as
`{{ vars.<name> }}`. Consumers set `[bundles.<bundle>.variables]`.

Done when `uv run devkit bundle validate <bundle dir>` passes.
