---
id: CAP-HARN-command-design
title: Command Creation Guidance
summary: "Opt-in catalog instructions for choosing necessary justfile, CLI and MCP entry points before creating or extending them."
area: harness
status: active
usecases: [UC-design-command-entrypoints]
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/command_design/bundle/instructions/command-design.md
---

# [CAP-HARN-command-design] Command Creation Guidance

## 1. Scope

The `command-design` bundle in devkit-catalog guides agents creating, configuring or extending justfile recipes,
CLI commands and MCP tools. It adds no runtime code. CAP-CLI-agent-cli-toolkit owns Python CLI implementation;
CAP-GATE-commit-gates owns command execution; CAP-DLV-review-refactor owns requested cleanup of existing interfaces.

## 2. Behavior

1. **Selection**: The bundle MUST remain opt-in with one `core` preset containing one instruction and no guidance,
   skill projection, rule or automatic configuration (`packages/devkit-catalog/tests/integration/bundles/test_bundles.py`).
2. **Conditional context**: The instruction description MUST identify creation, configuration and extension as its
   reading trigger; the body is loaded only when relevant through the existing context mechanism.
3. **Purpose**: Before adding an entry point, the agent SHOULD identify its operation, caller and existing execution
   path, reusing that path when it meets the caller's needs.
4. **Distinct entry points**: The agent SHOULD add a wrapper or alias only for useful task composition, required
   execution context or a distinct caller contract.
5. **Interfaces**: The instruction SHOULD preserve established recipe names, keep commit checks fast and explicit,
   avoid duplicate hook checks, keep specialized help discoverable, and select MCP tools by caller needs rather
   than mirroring every CLI command.
6. **Compatibility**: Extending an interface SHOULD preserve existing public commands; removing one is a separate
   compatibility decision. Unused hypothetical tasks do not justify new placeholder commands.
7. **Verification**: The agent SHOULD verify retained entry points from their documented working directory with
   their required tools and confirm each addition has a purpose.

## 3. Interfaces

After installing devkit-catalog, `uv run devkit add command-design` selects the default `core` preset.
`uv run devkit get-context command-design` lists the instruction header and path without loading its body.
The bundle adds no CLI generator, MCP filter, task runner requirement or telemetry.
