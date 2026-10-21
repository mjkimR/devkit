---
name: resource-kinds
description: Read before choosing the kind of a new asset (rule, gate, skill, subagent, instruction, playbook, workflow, guidance, document or hook).
---

# Choosing an asset kind

Every asset has one `kind` in its bundle's `bundle.toml`, which decides where
it lands, who reads it when, and what it costs in context. Pick the kind from
what the content *is*, not from how often it is needed.

## Decision tree

```text
Can a program verify the invariant with certainty?
  yes -> rule            (Python, run by the rule engine of devkit-agt; zero agent tokens)
  no  -> Must it run at a Git hook stage and block a commit?
    yes -> gate          (Python, run by the commit gate of devkit-agt; zero agent tokens)
    no  -> Is it a reusable tool or script directory the agent executes?
      yes -> skill       (directory with SKILL.md, projected into agent skill directories)
      no  -> Is it a delegated persona for a subagent?
        yes -> subagent  (native file per agent, or one host-neutral role contract)
        no  -> Is it a procedure rather than a judgment criterion?
          yes, recurring multi-stage delivery flow -> workflow
          yes, occasional task                     -> playbook
          no  -> Is it the bundle's short orientation read before anything else?
            yes -> the bundle's AGENTS.md (constitution)
            no  -> instruction (default for policies, standards, judgment criteria)
```

Three kinds sit outside the tree: `document` (reference material read by path,
or with `seeded = true` a scaffold the project owns after the first sync),
`guidance` (a short line in the root `AGENTS.md` block that sends every session
to an instruction at a moment no skill marks, such as "before writing a commit
message") and `hook` (a handler the agent host calls at a native event).

## Comparison

| Kind | File form | Who consumes it, when | Context cost |
| --- | --- | --- | --- |
| `rule` | `rules/<slug>/`: a plugin package directory of `.py` modules, guide and tests | The rule engine of `devkit-agt` (checks, commit gate, CI); loaded from the receipt | none |
| `gate` | `gates/<slug>/`: a plugin package directory | The commit gate of `devkit-agt` at a Git hook stage | none |
| `skill` | `skills/<slug>/SKILL.md` or `SKILL.md.jinja`, and support files | The agent host lists it and invokes it as a tool; sync opens the body with the bundle context prerequisite, so never write it | name and description always; body on invocation |
| `subagent` | native file per agent or `subagents/<slug>.md` contract | The host loads it when delegating | persona on load |
| `workflow` | one Markdown definition with `id` and `stages` | The generated `devkit-workflow` entry skill, backed by the workflow engine of `devkit-agt` | stage output only |
| `playbook` | `playbooks/<slug>.md` or directory with `SKILL.md` | Explicit discovery, rule remediation, or an exact ID named for the task/schedule | selected headers then body, or exact body |
| constitution | `AGENTS.md` at the bundle root | Returned whole by `get-context`, once per bundle | the whole file; keep it short |
| `instruction` | `instructions/<slug>.md` with `name` and `description` frontmatter | Header returned by `get-context`; body read when relevant | header always, body on demand |
| `document` | any files | Agents read the managed copy by path; a seeded one is project-owned after the first sync | only when read |
| `hook` | one TOML definition (`host`, `event`, `handler`, optional `matcher`, `timeout`) | The selected host invokes an installed `devkit_dist.features.host.handlers` callable | native response only |
| `guidance` | one Markdown file of list items, at most 300 bytes; `{path:<asset-id>}` names another asset's file | Rendered into the root `AGENTS.md` block, read by every session | every turn: keep it to a pointer with its read condition |

## Boundaries that are easy to get wrong

- **Instruction versus playbook.** An instruction states criteria that apply
  while working and is visible in the catalog; a playbook is a numbered
  procedure for an occasional task, invisible until invoked. "Compatibility
  rules for schema changes" is an instruction; "recover a broken replica" is a
  playbook. A procedure followed for every delivery, with stages and approval
  gates, is a workflow.
- **Instruction versus rule.** If a check can be decided mechanically, write a
  rule, even if a sentence would be shorter: rules cost no tokens and run in gates.
- **Constitution versus instruction.** The constitution is read in full every
  time the bundle's context loads, so it holds only what every task needs.
- **Skill versus instruction.** A skill has steps the agent executes; one that
  only contains guidance is an instruction, unless the host must list it as a tool.

## Authoring requirements

- Frontmatter and headers are English. A `description` says *when to read* the
  document, not what it contains: the agent decides from the header alone.
- A skill only the user should start (a release, a destructive cleanup)
  declares `invocation = "user"` in `bundle.toml`, never a host setting in the
  skill source.
- Slugs are lowercase with hyphens. Rule ids are unique across all bundles a
  repository installs; a later rule with the same id replaces an earlier one.
- The `harness-assets` instruction of the `harness` bundle covers the modules,
  imports and tests of rule, gate and workflow assets.
- `devkit bundle validate` checks the remaining manifest and frontmatter requirements.

## Configurable Markdown

Instruction, guidance, document and skill assets may use `.md.jinja` sources.
Declare each input under `[variables.<name>]` with `type = "string"`,
`"boolean"` or `"integer"` and an optional `default` (needed for a local
`bundle plan` without project inputs), and use `{{ vars.<name> }}` in the
template; consumers set `[bundles.<bundle>.variables]` in `.devkit/config.toml`.
Guidance limits apply after rendering.
