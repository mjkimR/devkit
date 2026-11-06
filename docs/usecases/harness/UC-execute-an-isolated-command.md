---
id: UC-execute-an-isolated-command
title: Execute an Isolated Native Command
summary: "An AI coding agent starts a native command at a fixed commit, continues independent work and collects retained execution evidence with optional guarded cleanup."
area: harness
primary_actor: AI coding agent
supporting_actors: []
status: active
capabilities:
  - CAP-HARN-isolated-execution
entrypoints:
  - packages/devkit/src/devkit_agt/features/isolated_execution/cli.py
---

# [UC-execute-an-isolated-command] Execute an Isolated Native Command

## 1. Goal

- **Goal**: Collect command evidence for a fixed commit while continuing independent work.
- **Scope**: harness isolated execution.
- **Trigger**: a native verification/build command is ready.
- **Preconditions**: the caller has authority for checkout/setup/native effects and has isolated shared external resources.

## 2. Main Success Scenario

1. The agent requests execution of its native command at a fixed commit (`CAP-HARN-isolated-execution`).
2. The system captures the definition and starts isolated preparation, returning execution identity (`CAP-HARN-isolated-execution`).
3. The agent starts observation and performs independent work (`CAP-HARN-isolated-execution`).
4. The system prepares the environment, executes the command and persists evidence (`CAP-HARN-isolated-execution`).
5. The system returns the collected result and any requested guarded cleanup outcome (`CAP-HARN-isolated-execution`).
6. The agent applies the result only to the tested commit and scope (`CAP-HARN-isolated-execution`).

## 3. Extensions

- **1a. Invalid commit/argv**: the system refuses with `EXECUTION_ARGUMENT_INVALID` or `EXECUTION_REF_UNKNOWN`; the use case ends.
- **4a. Preparation/native failure**: the system retains failure evidence and returns a negative result; resumes at step 5.
- **4b. Lost process ownership**: the system reports unknown and retains the checkout; the use case ends.
- **3a. Wait timeout/interruption**: observation stops without cancelling execution; the agent may resume at step 3.
- **3b. Cancellation requested**: the system confirms managed shutdown and retains the checkout; resumes at step 5.
- **5a. Unsafe cleanup**: the system reports `EXECUTION_CLEAN_REFUSED` separately and retains the execution result and environment; resumes at step 6.

## 4. Postconditions

- **Success guarantee**: durable evidence names the executed commit and actual native outcome; eligible requested cleanup preserves it.
- **Minimal guarantee**: unknown execution never passes and unsafe cleanup preserves the checkout; waiting never implicitly cancels execution.

## 5. Acceptance Criteria (Given / When / Then)

### Scenario 1: Collect fixed-commit evidence

- **Covers**: main success scenario
- **Given** a command waiting on a test-owned latch at commit A.
- **When** the agent launches it, completes independent work, advances main and releases the latch.
- **Then** retained output reflects A and is readable after guarded cleanup.

### Scenario 2: Invalid definition

- **Covers**: 1a
- **Given** an unavailable commit or absent native argv.
- **When** execution is requested.
- **Then** the command refuses and no native execution occurs.

### Scenario 3: Preparation and native failure

- **Covers**: 4a
- **Given** failing setup or a native command exiting seven.
- **When** the result is collected.
- **Then** setup failure prevents native execution, or native exit seven remains in retained failure evidence.

### Scenario 4: Unknown ownership

- **Covers**: 4b
- **Given** missing terminal evidence and a lost/reused supervisor identity.
- **When** the agent waits or cleans.
- **Then** unknown execution cannot pass or authorize checkout removal.

### Scenario 5: Interrupted observer

- **Covers**: 3a
- **Given** an active execution.
- **When** its waiter times out or is interrupted.
- **Then** execution continues and its checkout remains.

### Scenario 6: Managed cancellation

- **Covers**: 3b
- **Given** a nested wrapper and surviving child.
- **When** cancellation is requested.
- **Then** cancellation is confirmed only after managed writers exit and retains the checkout.

### Scenario 7: Unsafe cleanup

- **Covers**: 5a
- **Given** a passed run whose checkout contains unexpected untracked diagnostics.
- **When** cleanup is requested.
- **Then** its passing execution result is preserved separately from the cleanup refusal and diagnostics remain.
