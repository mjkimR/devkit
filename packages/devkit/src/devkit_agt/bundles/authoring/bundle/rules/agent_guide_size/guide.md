# [RULE-agent-guide-size] Agent Guide Size Budget

## 1. Overview

Agent guides (`AGENTS.md`, `CLAUDE.md`) are loaded into every agent turn, so every byte costs context on every
request. The rule warns when a guide outgrows its budget, so what only some tasks need moves to where it is read on
demand.

- **Phase and severity**: `hygiene`, `warning`; runs under `devkit rules check --phase hygiene` only. Shipped by the
  opt-in `authoring` bundle (preset `agent-guide-authoring`).
- **What is checked**: the targeted files matching `paths` (default `**/AGENTS.md`, `**/CLAUDE.md`) and not
  `exclude` (default `**/bundle/AGENTS.md`: a bundle constitution is read once through `devkit get-context`, not on
  every turn). A symlinked guide (`CLAUDE.md` pointing at `AGENTS.md`) is measured once, through its target.

## 2. Cause of Violation

- A guide is larger than `max_bytes` UTF-8 bytes (default 8192). The message gives its size and, for the root
  `AGENTS.md`, the share of the guidance block `devkit sync` writes between `<!-- DEVKIT:START -->` and
  `<!-- DEVKIT:END -->`: `Guide has <n> bytes, including <m> bytes of the devkit guidance block; effective max_bytes
  is <max>`.
- The whole file counts, the guidance block included. `@path` imports inside `CLAUDE.md` are not followed; count an
  imported file yourself when a host expands it.

## 3. Remediation

Curate the guide by the `agent-guide-authoring` playbook (`uv run devkit playbook search "curate agent guide"`):
keep what nearly every task needs and move the rest to where it is read on demand. Shrink the guidance block only by
deselecting presets that contribute `guidance` fragments. The rule never rewrites files.

## 4. Configuration

| Setting | Type | Default | Meaning |
| --- | --- | --- | --- |
| `max_bytes` | positive integer | `8192` | Bytes allowed per guide. |
| `paths` | list of patterns | `["**/AGENTS.md", "**/CLAUDE.md"]` | Files measured. |
| `exclude` | list of patterns | `["**/bundle/AGENTS.md"]` | Files never measured. |

```toml
# Nested guides get a smaller budget.
[[rules.settings.RULE-agent-guide-size.overrides]]
path = "packages/**/AGENTS.md"
max_bytes = 4096
```

Patterns are workspace-relative; a standalone `**` matches zero or more path segments.

## 5. Exceptions

Record a justified exception as an exact-path override with the reason in a comment directly above it, and remove it
when the guide shrinks.
