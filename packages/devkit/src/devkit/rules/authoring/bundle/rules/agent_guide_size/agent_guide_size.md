# [RULE-agent-guide-size] Agent guide size warning

Agent guides (`AGENTS.md`, `CLAUDE.md`) are loaded into every agent turn, so
each byte costs context on every request. A guide larger than the effective
`max_bytes` receives a warning with its size and the limit. The rule never
rewrites files. The full procedure is the `agent-guide-authoring` playbook of
the `authoring` bundle (`uv run devkit playbook search "curate agent guide"`).

This is a hygiene rule: it runs under `devkit rules check --phase hygiene` only.

## What the size includes

The whole file is measured, including the guidance block `devkit sync` writes
into the root `AGENTS.md` between `<!-- DEVKIT:START -->` and
`<!-- DEVKIT:END -->`; the message reports the block's share. The block is
regenerated on every sync: shrink it by deselecting presets that contribute
`guidance` fragments, never by editing it. A symlinked guide (for example
`CLAUDE.md` pointing at `AGENTS.md`) is measured once, through its target.
`@path` imports inside `CLAUDE.md` are not followed; count imported files
yourself when a host expands them.

## Remediation

Drop project structure trees: they are large, change with every file and go
stale; a one-line-per-module map with links is enough. Move other content to
where it is read on demand:

- module-specific conventions, commands, layout or architecture: the module's
  README or `docs/`, with at most a conditional link left in the guide;
- judgment rules for a kind of work: an instruction;
- multi-step procedures: a playbook or skill;
- mechanically checkable invariants: a rule;
- guidance for one directory: a nested guide in that directory.

Keep orientation, boundaries, invariants, verification commands and pointers
whose read condition is explicit.

## Configuration

Defaults: `max_bytes = 8192`, `paths = ["**/AGENTS.md", "**/CLAUDE.md"]` and
`exclude = ["**/bundle/AGENTS.md"]` (bundle constitutions are read once per
bundle through `devkit get-context`, not on every turn). Record a justified
exception as an exact-path override with the reason in a comment:

```toml
# Nested guides get a smaller budget.
[[rules.settings.RULE-agent-guide-size.overrides]]
path = "packages/**/AGENTS.md"
max_bytes = 4096
```
