---
id: PROP-mcp-runtime-pending
title: Report MCP registration pending only when runtime state warrants it
summary: Distinguish unavailable MCP runtimes from actionable registration work while keeping status provider-free and invalidating stale observations.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-28
target_area: capabilities/mcp/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-dist/src/devkit_dist/features/host/
    - packages/devkit-dist/src/devkit_dist/features/distribution/
    - docs/capabilities/mcp/
  excludes:
    - packages/devkit-mcp/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-mcp-runtime-pending] Report MCP registration pending only when runtime state warrants it

## 1. Background & Hypothesis

Status repeatedly emits MCP_REGISTRATION_PENDING although registration reports MCP_RUNTIME_UNAVAILABLE. Status deliberately avoids loading the registration provider.

## 2. Technical Spike Questions

- **Q1**: How can provider-free status distinguish unavailable runtime from actionable registration work?
- **Q2**: If a registration observation is retained, what invalidates it after runtime installation or configuration changes?

## 3. Proposed Design & Impact

Compare provider-free observation strategies against CAP-MCP-runtime-registration. Preserve actionable pending notices after runtime availability changes. Do not install a runtime, write external host configuration or indefinitely suppress pending notices during Planning.

## 4. Lifecycle & Retirement Criteria

Choose a bounded observation/invalidation contract with scenarios for unavailable, subsequently available and changed runtime or host configuration. Keep ordinary status provider-free unless a justified contract change is explicitly proposed.

## Source feedback

- `FB-mcp-registration-pending-ignores-runtime`: resolve the recorded problem through this proposal; no implementation is authorized before plan acceptance and handoff.
