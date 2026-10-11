# Agent Native Adapters and Projection

**Status**: Architecture Specification & Reference Implementation  
**Package**: `devkit-distribution`  
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
| `codex` | `subagent` | `.codex/agents/<asset-id>.toml` | `variants.codex` single `.toml` file |
| `claude-code` | `skill` | `.claude/skills/<asset-id>/` | Common `source` or `variants.claude-code` directory |
| `claude-code` | `subagent` | `.claude/agents/<asset-id>.md` | `variants.claude-code` single `.md` file |

---

## 3. Multi-Agent Projection Semantics

- **Shared Skills**: Skills are directory-based assets. The entire source directory (including supporting references and executable scripts) is projected into `.agents/skills/<asset-id>/` for Codex and `.claude/skills/<asset-id>/` for Claude Code. Executable permissions (`0755`) are preserved.
- **Native Subagents**: Subagents require an explicit native file for each target agent. Codex requires a `.toml` configuration file; Claude Code requires a `.md` markdown definition.
- **No Lossy Downgrades**: If a selected agent does not have a native variant defined for a subagent, synchronization fails immediately with an explicit error. The distributor never attempts heuristic conversions or parameter stripping.
- **Target Selection**:
  - `devkit sync --agent codex`: Projects assets for Codex.
  - `devkit sync --agent codex --agent claude-code`: Projects assets for both agents simultaneously.
  - `devkit sync --no-agents`: Clears native agent selections and safely unlinks unchanged native projections while keeping managed resources intact.
  - Running `devkit sync` without `--agent` preserves previously recorded agent selections from the receipt or uses `.devkit/config.toml`.

---

## 4. Host Environment Boundaries

- **Bootstrap Instructions**: Instructions (`kind = "instruction"`) and playbooks (`kind = "playbook"`) remain in `.devkit/managed/<bundle>/` and are recorded in the receipt's asset index. Discovered via `devkit list` and progressive context loading.
- **No Host Mutation**: The distributor does not automatically modify host system settings, user credentials, agent trust configurations, or global instruction files (e.g., `AGENTS.md` or `CLAUDE.md`). Session integration is handled explicitly by developer configuration or entry point linking.
