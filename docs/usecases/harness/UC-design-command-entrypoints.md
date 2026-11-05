---
id: UC-design-command-entrypoints
title: Design Necessary Command Entry Points
summary: "An AI coding agent creates or extends project commands using identified operations and callers while reusing suitable existing entry points."
area: harness
primary_actor: AI coding agent
supporting_actors: []
status: active
capabilities: [CAP-HARN-command-design]
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/command_design/bundle/instructions/command-design.md
---

# [UC-design-command-entrypoints] Design Necessary Command Entry Points

## 1. Goal

- **Goal**: Provide useful project entry points without unnecessary commands or duplicated checks.
- **Scope**: The command-design instruction.
- **Trigger**: A request to create, configure or extend a justfile, CLI or MCP interface.
- **Preconditions**: The project has selected the bundle and supplies its implementation conventions.

## 2. Main Success Scenario

1. The agent reads the relevant creation instruction (CAP-HARN-command-design).
2. The agent identifies the requested operation, caller and existing execution path (CAP-HARN-command-design).
3. The agent selects the necessary additions using the relevant interface guidance (CAP-HARN-command-design).
4. The agent implements and verifies those additions from their documented execution context (CAP-HARN-command-design).

## 3. Extensions

- **3a.** Existing command suffices: The agent reuses it and proceeds to verification in step 4 without adding a wrapper.
- **3b.** Removing a public command is proposed: The agent separates that compatibility decision from creation;
  this use case ends without removing the command.

## 4. Postconditions

- **Success guarantee**: Each added entry point has an identified operation and caller and a verified execution context.
- **Minimal guarantee**: The instruction itself registers or deletes no commands or tools.

## 5. Acceptance Criteria

### Scenario 1: Create an entry point
- **Covers**: main success scenario.
- **Given**: A concrete operation needs access through MCP.
- **When**: The agent applies the instruction.
- **Then**: It selects that operation instead of mirroring unrelated CLI commands and verifies the resulting tool.

### Scenario 2: Reuse native verification
- **Covers**: 3a.
- **Given**: A fast native command already serves the commit check.
- **When**: The agent configures verification.
- **Then**: It uses that command without adding a redundant justfile wrapper or duplicate hook check.

### Scenario 3: Preserve public compatibility
- **Covers**: 3b.
- **Given**: An existing public command is unused by the current task.
- **When**: The agent extends the interface.
- **Then**: It does not delete that command based only on the current task's usage.
