---
id: UC-record-a-maintenance-run
title: Record a maintenance run
summary: "A maintenance agent freezes inspected content and report evidence, then separately publishes an authorized durable history record."
area: governance
primary_actor: AI coding agent
supporting_actors: [human approver, GitHub]
status: proposed
capabilities: [CAP-DLV-maintenance-history]
---

# [UC-record-a-maintenance-run] Record a maintenance run

## 1. Goal

- **Goal**: retain verifiable maintenance evidence independently of conversation and code history.
- **Scope**: maintenance run history.
- **Trigger**: a maintenance playbook begins with a fixed report path.
- **Preconditions**: the agent has a bounded maintenance scope.

## 2. Main Success Scenario

1. The agent fixes the report destination and requests an inspected-content record (`CAP-DLV-maintenance-history`).
2. The system captures content identity without changing the checkout (`CAP-DLV-maintenance-history`).
3. The agent writes and verifies its maintenance report (`CAP-DLV-maintenance-history`).
4. The system freezes the report and registered evidence after checking secrets (`CAP-DLV-maintenance-history`).
5. The human selects and authorizes a history publication destination (`CAP-DLV-maintenance-history`).
6. The system publishes one atomic record and returns its history commit (`CAP-DLV-maintenance-history`).
7. The agent appends later integration state through a separately authorized amendment (`CAP-DLV-maintenance-history`).

## 3. Extensions

- **4a.** Evidence contains a secret: the system refuses HISTORY_SECRET_FOUND without finishing the record; remove the secret and resume step 4.
- **4b.** Inspected content changed: the system warns HISTORY_RUN_DRIFTED; revalidate the evidence and resume step 5.
- **5a.** Authority or destination is absent: preserve local evidence with publication pending; the use case ends.
- **6a.** A reference update response is lost: record HISTORY_PUBLISH_UNKNOWN, inspect through the same operation and resume step 6 only with its original bytes.
- **6b.** The branch is absent: record HISTORY_BRANCH_MISSING; request separate initialization authority and resume step 6.

## 4. Postconditions

- **Success guarantee**: immutable evidence and any amendments are retained on the selected history branch with a source-content identity.
- **Minimal guarantee**: report bytes and local Git refs/index remain unchanged; publication state is distinct from run outcome.

## 5. Acceptance Criteria (Given / When / Then)

### Scenario 1: Record and publish verified evidence
- **Covers**: main success scenario
- **Given** a finished maintenance report and authorized initialized destination.
- **When** the agent publishes the run.
- **Then** one history commit contains its canonical record, report and index line.

### Scenario 2: Refuse a secret before finish
- **Covers**: 4a
- **Given** report bytes containing a recognized credential.
- **When** finish checks evidence.
- **Then** HISTORY_SECRET_FOUND leaves finished_at unset.

### Scenario 3: Detect inspected-content drift
- **Covers**: 4b
- **Given** a source change after intake.
- **When** finish recaptures content.
- **Then** HISTORY_RUN_DRIFTED asks the agent to revalidate evidence.

### Scenario 4: Preserve local evidence without publication authority
- **Covers**: 5a
- **Given** no authority for an external destination.
- **When** publication is requested.
- **Then** HISTORY_AUTHORITY_MISSING leaves publication pending and makes no API call.

### Scenario 5: Resolve uncertain publication by content
- **Covers**: 6a
- **Given** the ref update succeeded but its response was lost.
- **When** the same operation retries.
- **Then** remote content inspection resolves published without another write.

### Scenario 6: Keep missing-branch publication pending
- **Covers**: 6b
- **Given** a readable repository without the history branch.
- **When** publication starts.
- **Then** HISTORY_BRANCH_MISSING preserves pending and creates no branch.
