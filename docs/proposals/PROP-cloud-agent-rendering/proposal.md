---
id: PROP-cloud-agent-rendering
title: Render cloud agent assets without MCP guidance
summary: "Make sync --cloud render CLI-only agent instructions without MCP routes, using execution-aware templates and coverage for constitution and subagent assets."
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-21
target_area: capabilities/distribution/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-dist/src/devkit/distribution/
    - packages/devkit-dist/tests/
    - packages/devkit-spec/src/devkit_spec/bundle/
    - docs/capabilities/distribution/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-cloud-agent-rendering] Render cloud agent assets without MCP guidance

## 1. Background & Hypothesis

`PROP-worker-shared-state-mcp` defines dual access to shared artifacts: MCP is the primary local route, and
CLI serves cloud execution. Local orchestration checks the MCP connection and asks the user to connect when it
is unavailable. Cloud agents should receive only the applicable CLI instructions, without MCP discovery,
connection, approval or fallback instructions.

Existing `devkit sync --cloud` records the execution environment but does not pass it into Jinja rendering.
Current template declarations support presentation language defaults, while constitution and subagent assets
are outside the supported templated kinds. Environment-aware output also affects local-render evidence and
repeat-sync behavior. Therefore complete cloud guidance removal needs a bounded distribution change and an
asset audit rather than a manually supplied template variable.

This proposal separates that work from shared artifact storage. It is queued for Planning; no rendering or
runtime policy change is authorized by this draft alone.

## 2. Technical Spike Questions

- **Q1 — Render inputs:** How should the existing execution environment become a deterministic Jinja input,
  resolved before inventory planning and included in render digests, receipts and drift checks?
- **Q2 — Asset coverage:** Which constitution, subagent, skill, reference and installation-guide surfaces carry
  MCP instructions? Which need templating support versus restructuring into already supported asset kinds?
- **Q3 — Projection and reversibility:** How does cloud sync remove earlier local MCP guidance and how does local
  sync restore it without mutating source bundles or causing cross-worktree configuration leakage?
- **Q4 — Bounded scope:** Can the selected design preserve current template validation, inventory constraints,
  personal rendering and host projection contracts? Present broad changes before committing to that direction.

## 3. Proposed Design & Impact

Use the existing sync execution-environment selection as the source for rendered agent guidance. Cloud output
exposes equivalent CLI operations only. Local output preserves MCP-first guidance and the local-orchestration
connection check owned by `PROP-worker-shared-state-mcp`. Rendering is presentation, not execution authority:
cloud runtime guards and human approval boundaries remain effective independently of text visibility.

Planning should identify exact source assets and distribution-owned changes, compare extending supported
kinds with moving conditional guidance into supported assets, and settle a testable meaning of MCP-free
agent output. The audit must include on-demand references and projected subagent instructions, not just the
root skill. Source repository implementation documentation may still describe MCP; hiding those files from
an agent with arbitrary repository read access is not the goal.

Expected acceptance evidence:

- A fresh `devkit sync --cloud` projects the selected bundles' executable agent guidance without MCP tool names,
  discovery/connection steps or MCP approval instructions, while retaining complete CLI workflows.
- A local-to-cloud-to-local sync sequence removes and restores environment-specific guidance deterministically;
  a repeated unchanged sync is idempotent and render receipts describe the actual environment.
- Constitution and subagent guidance are covered wherever the selected bundles expose them; missing asset-kind
  coverage is a failing check, not an undocumented exception.
- Local orchestration retains the connection check and requests user action when MCP is disconnected.
- Rendering tests cover environment selection, unsupported variables/kinds, language interaction, projection,
  receipt verification and personal-render constraints. Existing cloud execution restrictions still pass.

Non-goals: changing MCP runtime authorization, host trust or sandbox settings; enabling cloud integration
mutations; adding a remote shared-storage backend; hiding technical source files from repository inspection;
automatically starting this proposal's Development.

## 4. Lifecycle & Retirement Criteria

This is an independently queued follow-up to `PROP-worker-shared-state-mcp`, also relevant to
`SPEC-proposal-review-and-approval`. Planning should use the current distribution and execution-environment
contracts, preserve the shared-storage dependency boundary, and propose exact scope before implementation.
Planning and Development effort hints are medium because this introduces a cross-asset rendering contract.
