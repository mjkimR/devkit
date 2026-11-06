---
id: PADR-delivery-verification-routes
title: Separate local and cloud verification completion
summary: "For local and cloud delivery, we retain Host-collected local verification and complete client cloud PRs after required CI and merge, to reduce waiting, accepting nightly detection of broken cloud merge combinations."
proposal: PROP-async-e2e-verification
supersedes:
  - ADR-post-merge-verification
status: draft
created_at: 2026-11-06
---

# [PADR-delivery-verification-routes] Separate local and cloud verification completion

## 1. Context & Problem Statement

Devkit itself uses local-orchestrated delivery with an available Host. Client repositories can instead use cloud-pr
with no continuously available Host. `ADR-post-merge-verification` requires Host-collected landed verification
without distinguishing those completion policies. The accepted client cloud scenario tolerates broken combinations
until nightly detection; imposing a merged-result gate would change that scenario.

## 2. Decision Drivers

- Keep devkit's own local consumption separate from reusable client policy.
- Reduce local blocked time while retaining collected completion evidence.
- Permit client cloud batch delivery without a continuously available Host.
- Name the accepted stability exposure and actual CI/automation owner.

## 3. Considered Options

- Uniform synchronous landed verification: simple evidence, but blocks local progress and requires a cloud observer.
- Uniform nightly-only detection: low immediate cost, but discards the requested local verification responsibility.
- Distinct local and explicitly selected client cloud scenarios: selected; preserves local evidence and accepts
  delayed cloud integration-failure detection with consumer-owned recovery wiring.

## 4. Decision Outcome

- Devkit itself uses local-orchestrated verification; distributed guidance presents cloud-pr as a client scenario.
  → `CAP-HARN-agent-guidance` repository versus consumer verification guidance (MUST).
- Local completion retains fresh landed runtime synchronization and synchronous non-E2E/ancillary checks, with
  required selective E2E collected asynchronously before completion.
  → `CAP-DLV-delivery-workflows` section 4.8 local completion (MUST).
- Client cloud completion requires passing required PR CI including E2E and confirmed automatic merge, without
  latest-base prospective merge testing, forced refresh, merge queues or immediate postmerge CI.
  → `CAP-DLV-delivery-workflows` section 4.8 client cloud completion (MUST).
- Cloud clients accept broken merged combinations until nightly detection and repair. They name CI/automation
  ownership, cadence, missed-run visibility and rework/repair destinations before claiming automatic recovery.
  → `CAP-HARN-agent-guidance` consumer verification scenarios (MUST).
- Evidence names the actual tested revision and scope. A nightly repair is subsequent work, rather than a
  retroactive local pending-verification job for a completed cloud PR.
  → `CAP-DLV-delivery-workflows` section 4.8 completion evidence (MUST).
- This replaces `ADR-post-merge-verification` Host-led final-verification and before-handoff waiting clauses only
  for the selected client cloud scenario. Local obligations, Git/authority checks, runtime-based repair and the
  prohibition on automatic merge replay/rollback remain active. `CAP-DLV-proposal-planning` restates the
  corresponding cloud acceptance/handoff distinction during Development. The earlier ADR remains accepted with
  a partial-supersession note.
- An operational mode remains a transient invocation choice. Consumer policy declarations do not store a
  `cloud-pr` mode in project configuration or infer risk acceptance from a worker's machine.
  → `ARCH-04-2-delivery-policy` policy principles (MUST).

These restatement traces name planned Development changes; Planning does not claim that current contracts
already contain them.

## 5. Consequences

Local work can proceed during E2E but remains pending until required results are collected. Cloud main can be
broken between merge, nightly and repair. Clients own CI and dispatch integration; devkit adds no webhook or
client CI workflow here. A client without that wiring cannot claim automatic repair. Existing devkit CI remains
nightly/manual/release, with no cloud-pr adoption.

## 6. Confirmation

AC-2, AC-5, AC-6 and AC-9 through AC-12 in `PROP-async-e2e-verification` cover selection, local collection,
consumer cloud completion and truthful evidence. Guidance tests and explicit route walkthroughs check the
restatements. External client CI/dispatch activation is unverified in this repository and is consumer integration
work. Host execution and consumer operational compliance are Review only.
