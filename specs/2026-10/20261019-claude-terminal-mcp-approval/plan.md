---
id: PLAN-claude-terminal-mcp-approval
spec: SPEC-claude-terminal-mcp-approval
---

# Plan: Claude Code terminal MCP integration approval path

## 1. Invariant Review

Documentation only. `CAP-INT-mcp-services` authorization stays unchanged: only native `action=accept` with
`approve=true` grants authority, and the server checks the client's form capability rather than a host name
(`packages/devkit/src/devkit/host/mcp/server.py`). `ADR-integration-approval-asserted` is unaffected. The host
contract keeps `devkit host mcp setup` and `status` Codex-only; Claude Code owns its own registration writer, as Codex
does for its configuration.

## 2. Components and Interfaces

- `CAP-INT-mcp-services` §1 and §6: two supported terminal hosts, manual Claude registration, unverified surfaces.
- `guides/install/mcp.md`: host-neutral title, a Claude Code registration section beside the Codex adapter steps.
- `guides/INSTALL_GUIDE.md`, `guides/install/existing-repository.md`, `guides/install/new-repository.md`: route both
  hosts to the onboarding guide.
- `CAP-HOST-lifecycle-observation` §8 and summary, `docs/development/reference/host.md`: state the adapter scope.
- New `MAT-claude-terminal-mcp-approval-evidence`: the interactive run's observations.

No CLI, schema or bundle asset changes; the bundled `spec-integrate` guidance is already host-neutral
("when `devkit` MCP tools are available").

## 3. Verification

- `devkit rules check` and `devkit rules check --ci --base main` for references, summaries and spec lifecycle.
- `git diff --check`; manual check that every command and link in the changed text exists
  (`devkit host mcp config` output keys, `claude mcp add|get|remove` forms used in the run).
- Review at low effort in the session against the acceptance criteria.
