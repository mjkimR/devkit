---
name: resource-kinds
description: Read before adding a rule, skill, subagent, instruction, playbook, workflow, guidance fragment or commit gate to a repository. Decision tree and comparison of devkit asset kinds, how each is consumed, and what each costs in agent context.
---

# Choosing an asset kind

Every asset devkit distributes has one `kind` declared in its bundle's
`bundle.toml`. The kind decides where the file lands, when an agent or a tool
reads it and how many context tokens it costs. Pick the kind from what the
content *is*, not from how often it is needed.

## Decision tree

```text
Can a program verify the invariant with certainty?
  yes -> rule            (Python, run by devkit rules; zero agent tokens)
  no  -> Must it run at a Git hook stage and block a commit?
    yes -> gate          (Python, run by devkit gate; zero agent tokens)
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

Three kinds sit outside the tree: `workflow-check` (a Python check a workflow
definition names, run by `devkit workflow`), `document` (reference
material read by path, or with `seeded = true` a scaffold such as a docs tree
that the project owns and edits after the first sync) and `guidance` (a short
line in the root AGENTS.md block that sends every session to an instruction at
a moment no skill marks, such as "before writing a commit message").
```

## Comparison

| Kind | File form | Who consumes it, when | Context cost |
| --- | --- | --- | --- |
| `rule` | `rules/*.py` | `devkit rules check`, hooks, CI; loaded from the receipt | none |
| `gate` | `gates/*.py` | `devkit gate` at a Git hook stage | none |
| `skill` | `skills/<slug>/SKILL.md` and support files | The agent host lists it and invokes it as a tool; the body opens with the bundle context prerequisite | name and description always; body on invocation |
| `subagent` | native file per agent or `subagents/<slug>.md` contract | The host loads it when delegating | persona on load |
| `workflow` | one Markdown definition with `id` and `stages` | `devkit-workflow` entry skill and `devkit workflow next` | stage output only |
| `playbook` | `playbooks/<slug>.md` or directory with `SKILL.md` | Only on explicit `devkit-playbook` invocation or rule remediation | selected headers, then one body |
| constitution | `AGENTS.md` at the bundle root | Returned whole by `get-context`, once per bundle | about 50 to 100 lines |
| `instruction` | `instructions/<slug>.md` with `name` and `description` frontmatter | Header returned by `get-context`; body read when relevant | header always, body on demand |
| `workflow-check` | Python files (`BaseCheck` subclasses) | `devkit workflow` adds them to its check registry; loaded from the receipt | none |
| `document` | any files | Unseeded: a managed copy agents read by path. `seeded = true` with a `target`: written once into the project, then project-owned | only when read |
| `guidance` | one Markdown file of list items, at most 300 bytes; `{path:<asset-id>}` names another asset's file | Rendered into the root `AGENTS.md` block by `devkit sync`, read by every session | every turn: keep it to a pointer with its read condition |

## Boundaries that are easy to get wrong

- **Instruction versus playbook.** An instruction states rules, constraints
  and judgment criteria that apply while working; it is reachable from the
  catalog at any time. A playbook is a numbered procedure for an occasional
  task and is deliberately invisible until invoked. "Compatibility rules for
  schema changes" is an instruction; "recover a broken replica" is a playbook.
- **Playbook versus workflow.** A procedure the repository follows for every
  delivery, with stages and approval gates, is a workflow definition. A
  procedure that is reached for now and then is a playbook.
- **Instruction versus rule.** If a check can be decided mechanically, write a
  rule, even if a sentence in an instruction would be shorter. Rules cost no
  tokens and run in gates; prose is advisory.
- **Constitution versus instruction.** The constitution is read in full every
  time a bundle's context loads, so it holds only what every task needs:
  what the bundle is for, its hard contracts and which instructions exist.
  Everything that only some tasks need belongs in an instruction with a
  precise description, so the agent can decide from the header alone.
- **Skill versus instruction.** A skill is for doing: it has steps the agent
  executes and may ship scripts. A skill that only contains guidance should be
  an instruction, unless the host must be able to list it as a tool.

## Authoring requirements

- Frontmatter and headers are English. Instructions need `name` and
  `description` (every file of an instruction source; `devkit bundle validate`
  checks it); playbooks need `name`, `description` and optional `aliases`.
- A `description` says *when to read* the document, not what it contains.
  The agent decides from the header alone whether to open the body.
- Only skills and subagents take per-agent `variants`. A subagent role
  contract names all three agents under `hosts` (`status: unsupported` for an
  agent that gets no file); `devkit bundle validate` checks both.
- Slugs are lowercase with hyphens. Asset ids are unique within a bundle, and
  rule ids are unique across all bundles a repository installs; a later rule
  with the same id replaces an earlier one.
- Rules and gates are plain Python files that import only their engine's
  public API; the bundle package never imports them.
