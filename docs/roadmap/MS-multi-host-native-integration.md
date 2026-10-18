---
id: MS-multi-host-native-integration
title: Multi-host native lifecycle and integration across Claude Code, Codex, and Antigravity
summary: "Completes native host lifecycle observation and MCP integration approval across Claude Code, Codex, and Antigravity without relying on conversational CLI fallbacks."
status: planned
created_at: 2026-10-18
depends_on: []
---

# [MS-multi-host-native-integration] Multi-host native lifecycle and integration across Claude Code, Codex, and Antigravity

## Goal

Advances `ARCH-01-introduction-and-goals` §1.9 (Host & Scoped Integration) and §3.1 (Deterministic Execution) by completing host-native lifecycle observation (`CAP-HOST-lifecycle-observation`) and scoped MCP approval and integration services (`CAP-INT-mcp-services`) across Claude Code, Codex, and Antigravity, following up on `MAT-native-approval-host-comparison`.

## Exit condition

- Lifecycle observation hooks and host status inspection operate with verified parity across supported hosts.
- Scoped integration approval and execution (`devkit.integration`) complete through verified host-native MCP elicitation or host hook bindings without requiring the conversational local-CLI fallback path, with approval bound to the verified source and target commits.

## Non-goals

- **Scope Excluded**: External issue tracker or pull-request review bots, background daemon processes (`ARCH-01-introduction-and-goals` §3.4), and per-unit work lists (units declare membership through `milestone`).
