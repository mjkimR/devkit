# Agent Native Adapters and Projection

**Status**: Architecture Specification & Reference Implementation  
**Package**: `devkit`  
**Related Documents**:
- [Distribution Overview](overview.md)
- [Workspace Ownership & Overrides](workspace-ownership.md)
- [Resource Taxonomy](../architecture/resource-taxonomy.md)

---

## 1. Adapter Concept

AI coding agents use distinct directory structures, file formats, and subagent schemas. Adapters bridge the abstract bundle asset model to concrete vendor-specific directory hierarchies without forcing compromises on native configurations.

---

## 2. Agent Projection Matrix

| Agent | Target Kind | Destination Path in Project | Source Contract |
| --- | --- | --- | --- |
| `codex` | `skill` | `.agents/skills/<asset-id>/` | Common `source` or `variants.codex` directory |
| `codex` | `subagent` | `.codex/agents/<asset-id>.toml` | `variants.codex` single `.toml` file, or rendered from the `source` contract's `hosts.codex` block |
| `claude-code` | `skill` | `.claude/skills/<asset-id>/` | Common `source` or `variants.claude-code` directory |
| `claude-code` | `subagent` | `.claude/agents/<asset-id>.md` | `variants.claude-code` single `.md` file, or rendered from the `source` contract's `hosts.claude-code` block |
| `antigravity` | `skill` | `.agents/skills/<asset-id>/` | Common `source` or `variants.antigravity` directory (shared with Codex; identical bytes are written once) |
| `antigravity` | `subagent` | `.agents/agents/<asset-id>.md` | `variants.antigravity` single `.md` file, or rendered from the `source` contract's `hosts.antigravity` block (with `subagent: true`, `mainAgent: false`) |

---

## 3. Multi-Agent Projection Semantics

- **Shared Skills**: Skills are directory-based assets. The entire source directory (including supporting references and executable scripts) is projected into `.agents/skills/<asset-id>/` for Codex and `.claude/skills/<asset-id>/` for Claude Code. Executable permissions (`0755`) are preserved.
- **Native Subagents**: A subagent declared with `variants` ships an explicit native file per agent it supports; `variants` keys must be supported agent names. Codex requires a `.toml` configuration file; Claude Code and Antigravity require a `.md` markdown definition.
- **No Lossy Downgrades**: The distributor never attempts heuristic conversions or parameter stripping. A subagent declared with `variants` that has no file for a selected agent is simply not projected for that agent; `devkit sync` reports it under `unprojected` (a `[NOTICE: ...]` line on stderr) so the author can add the variant, ship a role contract, or the project can narrow `agents`.
- **Shared Directories**: Codex and Antigravity both read `.agents/skills/`. When both are selected, identical skill projections (including the generated `devkit-playbook` and `devkit-workflow` skills) are written once and stay in place while either agent remains selected; differing bytes for the same path are a collision error.
- **Role Contracts**: A subagent declared with a single `source` file is a host-neutral role contract. Its `hosts` table holds one explicit block per agent; projection renders that block deterministically (frontmatter keys for Claude Code, TOML keys plus `developer_instructions` for Codex) and prefixes the prompt with the contract's managed path, its procedure skill and the host status. This is not a conversion: only keys from the host's allowlist are accepted, a host with `status: unsupported` gets no file, and an agent the contract does not mention fails synchronization. `emulated` and `unverified` projections carry a sentence telling the agent that the host does not enforce the boundaries itself.
- **Extension Keys**: A contract may carry frontmatter keys of the form `x-<name>` (`x-[a-z][a-z0-9-]*`, any YAML value) for tools built on devkit, for example `x-model-profile` or `x-git-actions`. devkit validates the key shape only: it never renders an extension key into a projection and never interprets it. The keys stay readable in the managed copy of the contract (and in `read_contract(...).extensions` for library callers). Any other unknown key is still rejected.

- **Target Selection**:
  - By default every supported agent (`codex`, `claude-code`, `antigravity`) is a projection target: a project that never sets `agents` gets native copies for all three.
  - `devkit sync --agent codex`: Narrows projection to Codex; `--agent codex --agent claude-code` selects two.
  - `devkit sync --no-agents`: Records `agents = []`, which turns projection off and safely unlinks unchanged native projections (and the directories they leave empty) while keeping managed resources intact.
  - `devkit bundle plan <source> [--agent <name>]...` previews every projection a bundle source produces before it is installed.
  - `--agent` and `--no-agents` record the selection as `agents` in `.devkit/config.toml` (unless `--no-save`). Running `devkit sync` without them uses `.devkit/config.toml`.

### Role Contract Format

```markdown
---
role: reviewer                      # equals the asset id and the projected file name
title: Reviewer
description: Reviews a change against its specification and returns findings with evidence.
skill: review                       # optional: the procedure the role executes
hosts:
  claude-code:
    status: native                  # native | emulated | unsupported | unverified
    tools: [Read, Grep, Glob]       # allowed: tools, disallowedTools, model, permissionMode, maxTurns,
                                    #   skills, memory, background, omitClaudeMd, effort, isolation, color
  codex:
    status: emulated
    sandbox_mode: read-only         # allowed: model, model_reasoning_effort, sandbox_mode
  antigravity:
    status: native
    tools: [view_file, grep_search] # allowed: tools, model, commandExecutionPolicy, skills, plugins
    commandExecutionPolicy: "off"
---
# Reviewer
... the prompt, verbatim ...
```

Values are strings, integers, booleans or lists of strings. The rendered `description` (`<title>. <description>`) is a quoted scalar whose line breaks are escaped, never folded. Because every supported agent is a target by default, a contract should name all three hosts (use `status: unsupported` for a host that gets no file). The contract stays under `.devkit/managed/<bundle>/` and may be overridden like any asset; the projection then cites the override path.

---

## 4. Host Environment Boundaries

- **Bootstrap Instructions**: Instructions (`kind = "instruction"`) and playbooks (`kind = "playbook"`) remain in `.devkit/managed/<bundle>/` and are recorded in the receipt's asset index. Discovered via `devkit list` and progressive context loading.
- **No Host Mutation**: The distributor does not modify host system settings, user credentials, agent trust configurations, or user-level instruction files. The one project file it touches outside `.devkit/` and the agent directories is the root `AGENTS.md`, and only the marker-delimited guidance block in it (`<!-- DEVKIT:START -->` ... `<!-- DEVKIT:END -->`); see [Workspace Ownership, section 2](workspace-ownership.md#2-ownership-categories-and-invariants). `CLAUDE.md` is never written: Claude Code reads `AGENTS.md` through the project's own `CLAUDE.md` pointer or symlink, which stays developer-owned.
