---
id: UC-find-the-latest-maintenance-run
title: Find the latest maintenance run
summary: "A maintenance agent finds prior run outcomes and reads published evidence without fetching or modifying its local checkout."
area: governance
primary_actor: AI coding agent
supporting_actors: [GitHub]
status: active
capabilities: [CAP-DLV-maintenance-history]
entrypoints:
  - packages/devkit/src/devkit_agt/features/maintenance_history/cli.py
  - packages/devkit/src/devkit_agt/features/maintenance_history/usecases/operations.py
---

# [UC-find-the-latest-maintenance-run] Find the latest maintenance run

## 1. Goal

- **Goal**: compare a maintenance run with relevant prior evidence.
- **Scope**: maintenance history retrieval.
- **Trigger**: the agent needs an earlier report or integration outcome.
- **Preconditions**: the agent knows the relevant playbook and repository identity.

## 2. Main Success Scenario

1. The agent selects the playbook and optional source/outcome filters (`CAP-DLV-maintenance-history`).
2. The system reads newest history shards, merges amendments and omits superseded runs (`CAP-DLV-maintenance-history`).
3. The agent selects a listed run and its evidence file (`CAP-DLV-maintenance-history`).
4. The system returns published bytes without fetching or changing local Git state (`CAP-DLV-maintenance-history`).

## 3. Extensions

- **2a.** The history branch is absent: the system returns an empty result with a notice; the use case ends.
- **2b.** GitHub is rate limited: the system returns HISTORY_DEFERRED with retry_after; retry from step 2 later.
- **4a.** The run or file is absent: the system returns HISTORY_RUN_MISSING; choose another run at step 3.

## 4. Postconditions

- **Success guarantee**: the agent has the prior published evidence and latest known integration state.
- **Minimal guarantee**: retrieval changes no local index, refs, HEAD or evidence files.

## 5. Acceptance Criteria (Given / When / Then)

### Scenario 1: Merge amendments across year shards
- **Covers**: main success scenario
- **Given** multiple run years and later amendments.
- **When** the agent lists and reads a run.
- **Then** newest eligible runs include their latest integration state and returned files match published bytes.

### Scenario 2: Treat absent history as empty
- **Covers**: 2a
- **Given** no initialized history branch.
- **When** the agent lists prior runs.
- **Then** count is zero with a branch notice.

### Scenario 3: Defer limited reads
- **Covers**: 2b
- **Given** a rate-limited GitHub response.
- **When** history is listed.
- **Then** HISTORY_DEFERRED includes a retry time.

### Scenario 4: Refuse missing published evidence
- **Covers**: 4a
- **Given** no published file for the selected run.
- **When** the agent reads it.
- **Then** HISTORY_RUN_MISSING ends the read without local mutation.
