---
id: PROP-readiness-cli-runtime
title: Validate branch CLI contracts with an explicit readiness runtime
summary: Choose a safe way to validate changed CLI contracts during integration without confusing the retained base runtime with the source branch.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-28
target_area: capabilities/integration/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit/src/devkit_agt/features/rules/services/builtins/cli_contract/
    - packages/devkit-spec/src/devkit_spec/features/delivery/usecases/
    - docs/capabilities/integration/
  excludes:
    - packages/devkit-mcp/
task_kind: bugfix                     # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-readiness-cli-runtime] Validate branch CLI contracts with an explicit readiness runtime

## 1. Background & Hypothesis

Integration readiness checks the source snapshot with the retained base runtime. A branch adding CLI options can pass its own rules check but fail preparation against the base click tree.

## 2. Technical Spike Questions

- **Q1**: How can readiness distinguish source/runtime incompatibility from an invalid CLI citation without weakening checks?
- **Q2**: Should an explicit source-built runtime be required, or can deterministic CLI metadata supply equivalent evidence?

## 3. Proposed Design & Impact

Compare approaches against CAP-INT-mcp-services and the retained executor boundary. Preserve readiness, digest validation and the prohibition on executing the runtime inside a worktree being removed. Do not adopt skip-readiness or automatic source execution as a shortcut.

## 4. Lifecycle & Retirement Criteria

A reproducible CLI-addition case passes readiness under the chosen explicit runtime contract, while invalid citations still fail. Record any required contract change as a PADR before Development.

## Source feedback

- `FB-readiness-cli-contract-checks-the-base-runtime`: resolve the recorded problem through this proposal; no implementation is authorized before plan acceptance and handoff.
