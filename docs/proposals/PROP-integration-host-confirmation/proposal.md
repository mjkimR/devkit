---
id: PROP-integration-host-confirmation
title: Native integration confirmation on hosts beyond Codex
summary: Researches and adds native integration confirmation surfaces for Claude Code, Antigravity and other hosts that keep the binding to the request and never let the agent approve itself.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-19
target_area: integration/
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-multi-host-native-integration
boundaries:
  owns:
    - integration/
    - host/
    - packages/devkit-dist/src/devkit/host/
    - packages/devkit-spec/src/devkit_spec/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-integration-host-confirmation] Native integration confirmation on hosts beyond Codex

- **Split from**: `PROP-integration-follow-ups` (its question Q4), split during that proposal's Planning, which kept
  only the base advances. Created without `decomposed_from`: `devkit spec proposal new --decomposed-from` refuses a
  source in Planning (`SPEC_PROPOSAL_IN_PLANNING`).
- **Source feedback**: `FB-multi-host-integration-ergonomics`.
- **Related**: `CAP-INT-mcp-services`, `CAP-HOST-lifecycle-observation`, `ADR-integration-approval-asserted`,
  `MAT-native-approval-host-comparison`, `SPEC-claude-terminal-mcp-approval`.

## 1. Background & Hypothesis

Native integration confirmation runs through MCP form elicitation (`integration_integrate` with
`authority="mcp-elicitation"`). Hosts without elicitation, or without the projected `devkit` MCP server, get
`INTEGRATION_CONFIRMATION_UNAVAILABLE` and fall back to `devkit worktree finish <branch> --merge --local-only` after a
conversational approval.

What is already known (from the Planning of `PROP-integration-follow-ups`): the Claude Code terminal CLI is a
verified native path (`SPEC-claude-terminal-mcp-approval`, docs only), and the `Confirmation` callable in
`devkit.host.mcp` is host-agnostic form elicitation. What is left is research-led.

Hypothesis: each remaining host offers, or lacks, a confirmation surface that binds to `request.id` and the approved
scope and that the agent cannot answer itself; devkit adds setup and routing only where such a surface exists.

## 2. Technical Spike Questions

- **Q1 (Surfaces)**: which confirmation surfaces do Claude Desktop, the Claude Code VS Code extension, the Agent SDK,
  Antigravity and OpenCode offer, verified on each host, and which keep the binding to `request.id` and the approved
  scope without letting the agent approve itself?
- **Q2 (Setup)**: does a `devkit host mcp setup --host claude` adapter (and equivalents) belong in `devkit.host`, and
  what does it configure?
- **Q3 (Routing)**: how `spec-integrate` routes per host between native confirmation and the CLI fallback.

## 3. Proposed Design & Impact

To be designed in this proposal's Planning, in step with `MS-multi-host-native-integration`. The confirmation text
and binding come from `PROP-integration-follow-ups` (confirmation target and its descendants within one call).

## 4. Lifecycle & Retirement Criteria

- Preliminary decisions: `devkit spec proposal padr integration-host-confirmation "<title>" --summary "<what it decides>"`.
- Research: collect host evidence in `materials/`.
- On acceptance (`plan-accept`): hand off with `devkit spec proposal handoff integration-host-confirmation`.
- On rejection: `status: rejected` with the user's reason in the commit message.
