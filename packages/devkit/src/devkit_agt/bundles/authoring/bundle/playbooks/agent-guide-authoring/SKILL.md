---
name: agent-guide-authoring
description: Write or curate always-loaded agent guides (AGENTS.md, CLAUDE.md pointers, nested guides) and shrink one that grew too large (RULE-agent-guide-size), for example by removing a project structure tree.
---

# Agent guide authoring and curation

Use when you write or substantially edit an agent guide, or when `RULE-agent-guide-size` reports one;
`devkit rules explain RULE-agent-guide-size` gives the budget, the override syntax and how to shrink the devkit
guidance block. Read [host loading](references/hosts.md) when you add, move or point between guides (nested
guides, `CLAUDE.md`).

A guide loads on every turn, so it holds only what nearly every task needs.

## Step 1: Keep

- One or two lines of purpose.
- At most a module map: one line per module with its responsibility and a link to its README or docs.
- Boundaries and invariants an agent could break unknowingly.
- The verification commands to run before finishing.
- Safety, commit and publication constraints.
- Pointers with an explicit read condition ("Before changing schemas, read `docs/schema.md`."), because agents
  rarely follow a plain link.

## Step 2: Move or delete the rest

| Content | Destination |
| --- | --- |
| Structure trees, file inventories, counts, versions, implementation details | Nowhere: they go stale unnoticed, and agents list files themselves |
| Module-specific conventions, commands, layout or architecture | The module's README or `docs/`, or a nested guide in its directory |
| Judgment rules for one kind of work | An instruction |
| Multi-step or occasional procedures | A playbook or skill |
| Mechanically checkable invariants, or what a tool already enforces | A rule or the tool; drop the prose |
| What the agent host already instructs, history, narratives | Nowhere |

Write what stays as one precise sentence with a threshold or command, without emphatic wording.

## Completion conditions

- Every moved item exists at its destination, with a conditional pointer where an agent would not otherwise find it.
- No constraint that applies to every task left the guide.
- `uv run devkit rules check --phase hygiene` reports no `RULE-agent-guide-size` warning for the edited guides, or
  the guide has a commented override.
