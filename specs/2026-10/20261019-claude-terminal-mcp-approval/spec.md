---
id: SPEC-claude-terminal-mcp-approval
title: Claude Code terminal MCP integration approval path
summary: "Documents the Claude Code terminal CLI as a verified native MCP form-elicitation path for scoped integration approval, registered manually with claude mcp add."
status: completed
created: 2026-10-19
milestone: MS-multi-host-native-integration
related_capabilities:
  - CAP-INT-mcp-services
  - CAP-HOST-lifecycle-observation
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-claude-terminal-mcp-approval] Claude Code terminal MCP integration approval path

## 1. Problem Statement & Motivation

`CAP-INT-mcp-services` names the interactive Codex CLI as the only supported native approval path, and the
installation guides route MCP onboarding to Codex alone. An interactive Claude Code terminal session has since run
`integration_integrate` against the unchanged server and rendered its form for every outcome
(`MAT-claude-terminal-mcp-approval-evidence`). The documented contract understates the supported hosts, so an agent
in Claude Code is routed to the conversational CLI fallback although native approval works there.

## 2. User Stories

- **US-1**: As a developer using Claude Code in a terminal, I want to register the devkit MCP server and integrate
  through its native approval form so that local integration needs no conversational fallback.

## 3. Non-Goals

1. **Scope Excluded**: a Claude adapter for `devkit host mcp setup` or `status` (`--host claude`), changes to the MCP
   server or integration service, Claude Code hook (`PreToolUse` `ask`) approval, and support claims for Claude
   Desktop, the VS Code extension or the Agent SDK.
2. **Scope Excluded**: editing the dated `MAT-native-approval-host-comparison` research snapshot.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The integration contract names the verified Claude Code terminal path

- **Given** `CAP-INT-mcp-services`
- **When** an agent reads its supported path and setup sections
- **Then** they name the interactive Codex CLI and the interactive Claude Code terminal CLI as supported native form
  elicitation paths, cite `MAT-claude-terminal-mcp-approval-evidence`, state that Claude registration is manual, and
  keep auto mode, permission-prompt count, Claude Desktop, the VS Code extension and the Agent SDK as unverified.

### [AC-02] Onboarding gives exact Claude Code registration steps

- **Given** the optional MCP onboarding guide
- **When** a consumer's agent follows it for Claude Code
- **Then** it registers server `devkit` in Claude Code user scope with `claude mcp add --scope user devkit --` and the
  `command` and `args` printed by `devkit host mcp config --format json`, inspects it with `claude mcp get devkit`,
  removes it with `claude mcp remove devkit -s user`, and verifies tool discovery and the visible form in a new
  terminal session; the Codex steps are unchanged.

### [AC-03] Installation routes and host contracts name both hosts

- **Given** the installation guides, `CAP-HOST-lifecycle-observation` and the host reference
- **When** they route to or describe MCP onboarding
- **Then** they lead Codex and Claude Code users to the same onboarding guide and state that `devkit host mcp setup`
  and `status` adapt Codex only while Claude Code is registered with its own CLI.

### [AC-04] The verification evidence is retained

- **Given** the interactive Claude Code terminal run on 2026-10-19
- **When** the evidence material is read
- **Then** it records the host version, registration, task and the four observed outcomes with their Git effects,
  and lists what the run did not establish.
