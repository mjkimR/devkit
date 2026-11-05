---
id: UC-assess-test-management
title: Assess a selected test suite
summary: "An AI coding agent identifies a selected suite's coverage and resource risks and produces user-decided, scoped follow-up work without weakening native verification."
area: delivery
primary_actor: AI coding agent
supporting_actors: [Human approver]
status: active
capabilities:
  - CAP-DLV-test-management
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/test-management/SKILL.md
created_at: 2026-11-05
---

# [UC-assess-test-management] Assess a selected test suite

## 1. Goal

- **Goal**: find concrete suite coverage/resource problems and decide bounded follow-up work.
- **Scope**: the opt-in maintenance playbook.
- **Trigger**: the human invokes or confirms a selected-suite assessment.
- **Preconditions**: the agent can read the consumer repository.

## 2. Main Success Scenario

1. The agent records selected roots, inspected state and native verification contracts (`CAP-DLV-test-management`).
2. The agent inspects collection and resource prerequisites before executing safe bounded checks (`CAP-DLV-test-management`).
3. The agent compares coverage, isolation and applicable runner evidence with the consumer's requirements (`CAP-DLV-test-management`).
4. The agent presents findings and exact candidate scope for one human decision round (`CAP-DLV-test-management`).
5. The human decides dispositions and the agent routes approved work through the native workflow (`CAP-DLV-test-management`).
6. The agent reports actual outcomes, retained settings, destinations and remaining checks (`CAP-DLV-test-management`).

## 3. Extensions

- **2a. Required prerequisite unavailable or unknown**: leave the affected check not_run with an unmet gate;
  continue assessment of safe available evidence at step 3.
- **3a. Inconclusive tuning comparison**: retain current settings and report the evidence limit; continue at step 4.
- **4a. Unattended or unanswered decision**: report pending candidates with nothing applied; the assessment ends.

## 4. Postconditions

- **Success guarantee**: every approved candidate has a native-workflow destination and missing required checks
  remain visible; no approval was inferred from invocation.
- **Minimal guarantee**: no implicit consumer configuration, product data or integration-policy changes occur.

## 5. Acceptance Criteria (Given / When / Then)

### Native contracts and routing
- **Covers**: main success scenario
- **Given** a confirmed assessment and safe bounded evidence.
- **When** the human decides candidates.
- **Then** the report identifies exact scope, destinations, native gates and coverage limits.

### Missing required prerequisite
- **Covers**: 2a
- **Given** unavailable sockets or an unresolved database input.
- **When** the agent inspects prerequisites.
- **Then** the affected command stays unexecuted and its required gate is unmet.

### Inconclusive comparison
- **Covers**: 3a
- **Given** a parallel candidate with different collected identities or skips.
- **When** the agent compares it with serial execution.
- **Then** current settings remain and no speedup/default promotion is claimed.

### Unattended decision
- **Covers**: 4a
- **Given** proposed configuration edits without human decisions.
- **When** the run reaches the decision round.
- **Then** the report retains pending candidates and the consumer tree stays unchanged.
