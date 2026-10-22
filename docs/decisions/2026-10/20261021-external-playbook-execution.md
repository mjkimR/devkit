---
id: ADR-external-playbook-execution
title: External scheduling and exact playbook retrieval
summary: External systems own scheduling and callers execute playbooks; devkit retrieves synchronized procedures by exact identity without granting execution authority.
proposal: SPEC-exact-playbook-get
status: accepted
created_at: 2026-10-21
---

# [ADR-external-playbook-execution] External scheduling and exact playbook retrieval

- **Status**: Accepted
- **Date**: 2026-10-21

---

## 1. Context & Problem Statement

`MS-maintenance-operations` requires callers that already know a playbook ID to retrieve a task without discovery.
`ARCH-08-2-resource-taxonomy` currently describes explicit skill invocation or rule remediation as the entry
conditions. Scheduled invocation needs an explicit boundary that preserves task-specific authority.

## 2. Decision Drivers

Keep devkit focused on asset delivery, reuse synchronization and override integrity, retain explicit invocation,
and avoid inferring execution permission from successful retrieval or a recurring trigger.

## 3. Considered Options

1. Add a devkit scheduler and execution runtime: rejected; it adds persistent operational state, provider policy,
   retries and approval ownership outside the agreed task.
2. Require external runners to search or read an assumed managed path: rejected; search is unnecessary and paths
   bypass effective override and synchronization checks.
3. Provide exact receipt-backed retrieval, with scheduling and execution external: selected. The proposal defines
   the bounded result and errors; existing readers retain integrity and overrides.

## 4. Decision Outcome

Devkit provides `playbook get <bundle>/<playbook>` as a non-executing synchronized instruction retrieval contract.
External systems own scheduling and launching; the calling agent owns procedure execution, prerequisite checks
and progress. An explicitly configured schedule naming the exact ID is task-specific explicit invocation, as is
a user's direct request naming it. Neither grants extra permission or approval for gated operations. Ordinary
requests do not authorize discovery. Existing explicit discovery and failing-rule remediation remain valid.

The service reads the receipt's deployed snapshot and effective bytes through existing shared-lock readers;
it does not rediscover installed packages, synchronize implicitly, or offer fallback selection. It returns full
procedure body, canonical bundle/asset identity, effective path and byte hash, and context-loading requirements.
No package-source attestation is implied by that content hash.

## 5. Consequences

Callers can retrieve a known playbook without search dependencies. They must provide an appropriately synchronized
workspace, load required bundle context and preserve all project/host approval boundaries. Unavailable approval
UI does not authorize execution. Schedule retries, concurrency, history and recovery stay outside devkit.
The capability, resource taxonomy and consumption guidance must reflect explicit exact invocation consistently;
the existing no-unsolicited-discovery rule remains. No live scheduler integration proves or gates this decision.
