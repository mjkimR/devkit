---
id: MS-maintenance-run-history
title: Durable maintenance run history
summary: "Provides explicit opt-in maintenance run history kept apart from code history, with revision-linked records that an agent can publish, list and read without changing the local checkout."
status: done
created_at: 2026-10-26
depends_on: [MS-maintenance-operations]
---

# [MS-maintenance-run-history] Durable maintenance run history

## Goal

Advances `ARCH-01-introduction-and-goals` §1.3 (Delivery Workflow Orchestration) by letting a user explicitly retain
a maintenance run's outcome after the conversation ends. `CAP-DLV-maintenance-history` keeps revision-linked
records outside code history so later runs and people can compare them. Recording and publication are separate
explicit choices; the default playbooks remain independent, as `ADR-opt-in-maintenance-history` defines.

## Exit condition

- A user can explicitly capture and publish a maintenance run as a durable, revision-linked execution record kept
  apart from code history, with publication requiring authority for its destination.
- An agent can list and read those records without changing the local checkout.

## Non-goals

- **Scope Excluded**: A devkit scheduler, daemon or job registry; automatic history recording or publication;
  mandatory history steps or other changes to the default maintenance playbooks' procedures.

## Completion review

Decomposition: confirmed
Direct proposal work: confirmed
