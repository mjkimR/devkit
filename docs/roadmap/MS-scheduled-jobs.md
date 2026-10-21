---
id: MS-scheduled-jobs
title: Playbook entrypoint for externally scheduled execution
summary: "Delivers exact-ID playbook retrieval for external runners and an ADR that delegates scheduling to external systems, keeping scheduler implementation outside devkit's scope."
status: done
created_at: 2026-10-18
depends_on: []
---

# [MS-scheduled-jobs] Playbook entrypoint for externally scheduled execution

## Goal

Advances `ARCH-01-introduction-and-goals` §1.1 (Asset Distribution & Guidance Delivery) and §1.3
(Delivery Workflow Orchestration) by making a selected playbook easy for an external agent or scheduled runner to
retrieve and follow. External systems own scheduling; devkit provides the task retrieval contract. Maintenance
playbooks remain independently invocable, and their execution history belongs to `MS-maintenance-history`.

## Exit condition

1. A new `get` subcommand under `devkit playbook`, taking `<bundle>/<playbook>`, retrieves a synchronized playbook
   by its exact bundle and asset ID,
   without search or candidate selection. The result contains the procedure body, source identity, and required
   bundle-context loading information, respects effective overrides, and reports missing IDs through stable
   advisory codes. The command retrieves instructions; the calling agent executes them. Relevant verification and
   the CLI and playbook consumption contracts cover direct invocation by an external runner, including a user's
   explicitly configured scheduled invocation, while preserving existing workflow approval boundaries and the
   restriction on unsolicited playbook discovery. Output follows `ARCH-08-1-agent-output` and
   `CAP-ADV-agent-advisory-protocol`.
2. An accepted ADR establishes that scheduling is delegated to external systems and is outside devkit's scope.
   It defines devkit's responsibility as providing an explicit, readily consumable playbook entrypoint and task
   contract, with execution performed by the caller. The affected architecture and capability contracts and agent
   guidance reflect this boundary. No scheduler implementation or recurring-run demonstration is required to
   complete this milestone.

## Non-goals

- **Scope Excluded**: A devkit scheduler, daemon, job registry or schedule configuration; provider-specific schedule
  setup; cadence, dispatch, missed-run recovery, retries, overlap prevention or sequencing of scheduled jobs;
  executing playbooks inside the retrieval command; maintenance playbook authoring; durable execution history;
  and bypassing workflow approvals for unattended execution.
