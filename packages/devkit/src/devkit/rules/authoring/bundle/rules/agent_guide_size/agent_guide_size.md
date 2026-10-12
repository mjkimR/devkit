# [RULE-agent-guide-size] Agent guide size warning

Agent guides (`AGENTS.md`, `CLAUDE.md`) are loaded into every agent turn, so
each byte costs context on every request. A guide larger than the effective
`max_bytes` receives a warning with its size and the limit. The rule never
rewrites files. It runs under `devkit rules check --phase hygiene` only. The
full procedure is the `agent-guide-authoring` playbook of the `authoring`
bundle (`uv run devkit playbook search "curate agent guide"`).

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

Follow the `agent-guide-authoring` playbook: drop project structure trees (a
one-line-per-module map with links is enough) and move module-specific
content, judgment rules, procedures, checkable invariants and single-directory
guidance to where they are read on demand. Keep orientation, boundaries,
invariants, verification commands and pointers whose read condition is
explicit.

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
