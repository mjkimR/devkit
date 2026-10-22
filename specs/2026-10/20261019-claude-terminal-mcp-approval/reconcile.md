---
reconcile_id: REC-claude-terminal-mcp-approval
status: resolved
targets:
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
    resolution: modified
  - file: docs/capabilities/host/CAP-HOST-lifecycle-observation.md
    resolution: modified
  - file: docs/development/reference/host.md
    resolution: modified
  - file: docs/materials/2026-10/20261019-claude-terminal-mcp-approval/20261019-claude-terminal-mcp-approval-evidence.md
    resolution: modified
---

# Reconciliation: Claude Code terminal MCP integration approval path

`CAP-INT-mcp-services` names the Codex CLI and the Claude Code terminal CLI as supported native form-elicitation
paths, keeps Claude Code auto mode, prompt count and the Desktop, VS Code extension and Agent SDK surfaces unverified,
and gives the manual `claude mcp add|get|remove` registration. `CAP-HOST-lifecycle-observation` and the host
reference state that `devkit host mcp setup` and `status` adapt Codex only. `MAT-claude-terminal-mcp-approval-evidence`
retains the interactive run. The consumer guides (`guides/install/mcp.md`, the installation routes) mirror these
contracts. No code, schema or bundle asset changed, so entrypoints are unchanged and no story is affected.

No work is deferred: a Claude setup adapter and hook-based approval are non-goals with no retained requirement.
