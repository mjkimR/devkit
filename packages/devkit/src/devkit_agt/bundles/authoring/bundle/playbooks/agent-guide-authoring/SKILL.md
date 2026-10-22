---
name: agent-guide-authoring
description: Write or curate always-loaded agent guides (AGENTS.md, CLAUDE.md, nested guides) and shrink one that grew too large (RULE-agent-guide-size).
aliases:
  - curate agent guide
  - shrink AGENTS.md
  - agent guide size
  - write AGENTS.md
  - CLAUDE.md pointer
  - remove project structure tree
---

# Agent guide authoring and curation

Use this playbook when you write or substantially edit an agent guide, and when
`RULE-agent-guide-size` reports one. Read [host loading](references/hosts.md)
only when you add, move or point between guides (nested guides, `CLAUDE.md`).

Unlike a skill, a guide is loaded on every turn of every session, so it holds
only what nearly every task needs. Move other content to where it is read on
demand, not into references the guide links: agents follow a plain link unreliably.

## Prerequisites

- The guide to write or curate. Shrink the block between `<!-- DEVKIT:START -->`
  and `<!-- DEVKIT:END -->` only by deselecting presets that contribute
  `guidance` fragments.
- Curate as the task itself or in a hygiene session, not as a side quest.

## Step 1: Decide what stays

Keep only what applies to nearly every task in the directory the guide covers:

- one or two lines of purpose and orientation;
- at most a module map: one line per module stating its responsibility, with a
  link to its README or docs;
- architecture boundaries and invariants an agent could break unknowingly;
- the verification commands to run before finishing;
- safety, commit and publication constraints;
- pointers whose read condition is explicit ("Before changing schemas, read
  `docs/schema.md`."); a pointer without a condition is rarely followed.

Leave out, even when it looks helpful:

- **Project structure trees.** A tree is large and goes stale unnoticed;
  agents list files themselves, and the module map is enough orientation.
- **Module-specific content.** Conventions, commands, configuration, layout or
  architecture that apply to one module belong in that module's README or docs
  (or a nested guide in its directory). The root guide keeps at most a link
  with its read condition: "Before changing `packages/api`, read
  `packages/api/README.md`."

## Step 2: Move everything else to where it is read on demand

| Content | Destination |
| --- | --- |
| Module-specific conventions, commands, layout, architecture or API details | The module's README or `docs/`; the guide keeps a conditional link |
| Project or directory structure trees | Nowhere; keep the one-line-per-module map |
| Judgment rules for one kind of work | An instruction |
| Multi-step or occasional procedures | A playbook or skill |
| Mechanically checkable invariants | A rule (then drop the prose, or keep one line) |
| Guidance for one directory | A nested guide in that directory |

Leave a conditional pointer only when an agent would otherwise not find the
moved content at the moment it matters.

## Step 3: Write for every turn

- State invariants and decisions, not narratives or history.
- Leave out facts that drift: structure trees, file inventories, counts, version
  numbers, descriptions of current implementation details.
- Do not repeat what a tool already enforces or what the agent host already
  instructs; repetition costs context on every request.
- Write one precise sentence with a threshold or command instead of emphatic
  wording; capitals and absolute words make agents over-apply a rule.
- Keep one source of truth: when `CLAUDE.md` exists for Claude Code, point it at
  `AGENTS.md` instead of duplicating content (see references/hosts.md).

## Step 4: Record a justified exception

When a guide must stay large, add an exact-path override with the reason as a
comment directly above it in `.devkit/config.toml`:

```toml
# Monorepo root guide: shared boundaries for twelve packages; split planned.
[[rules.settings.RULE-agent-guide-size.overrides]]
path = "AGENTS.md"
max_bytes = 12288
```

## Completion conditions

- Every moved item is reachable: the destination exists and, where needed, a
  pointer with an explicit read condition remains.
- No constraint that applies to every task left the guide.
- `uv run devkit rules check --phase hygiene` reports no `RULE-agent-guide-size`
  warning for the edited guides, or the remaining guide has a commented
  override.
