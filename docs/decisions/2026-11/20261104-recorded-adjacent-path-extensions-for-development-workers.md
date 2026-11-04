---
id: ADR-recorded-adjacent-path-extensions-for-development-workers
title: Recorded adjacent-path extensions for development workers
summary: "For estimated worker write boundaries, we allow task-linked adjacent-path extensions and retain explicit hard denies, to avoid operator round trips, accepting semantic review of adjacency."
proposal: SPEC-worker-scope-extension
supersedes:
  - ADR-orchestration-workers
status: accepted
created_at: 2026-11-04
---

# [ADR-recorded-adjacent-path-extensions-for-development-workers] Recorded adjacent-path extensions for development workers

## 1. Context & Problem Statement

A required adjacent file may be absent from an estimated task boundary. Strict rejection stops the worker even
when the existing task and AC already require the change. A sync-output admission rule already demonstrates
recorded expansion with independent checks. `ADR-orchestration-workers` currently requires every write to be in
its payload scope and preserves a failed committed range for recovery.

## 2. Decision Drivers

- Complete the approved task without routine operator intervention for an adjacent file.
- Keep protected and explicitly denied paths outside self-admission.
- Make local and cloud worker/reviewer obligations identical.
- Preserve optional inspection and existing CLI/envelope compatibility.
- Avoid a generic ownership-policy engine for a semantic review decision.

## 3. Considered Options

1. Keep strict scope and ask the Host for every extra path: simple, but retains the interrupted work this addresses.
2. Derive adjacency through a new ownership registry and configurable deny patterns: mechanical, with recurring
   configuration and layering cost beyond the adjacent-file failure.
3. Record adjacent exact-file extensions and review necessity and ownership: bounded autonomy with a typed audit.
4. Permit any repository file needed by the worker: small, but admits unrelated feature and configuration work.

## 4. Decision Outcome

Option 3 is selected for bounded task continuity and proportionate verification.

- Development workers admit an exact adjacent file only for an existing task and AC, with a task annotation and
  matching typed worker extension record. Initial declared scope remains distinct from extension admission.
  → `CAP-DLV-delivery-workflows` worker write boundaries (MUST).
- Explicit payload denies prevail; protected classes and unrelated features require Host authority before writing.
  Test weakening, independent Git/sandbox restrictions and publication authority remain unchanged.
  → `CAP-DLV-delivery-workflows` worker write boundaries (MUST).
- Optional `scope_extensions` records carry path, task, reason and requirements; old envelopes remain valid.
  → `CAP-DLV-workflow-envelopes` worker fields (MUST).
- Inspection preserves its existing scope list and full-replacement flags and adds structural extension evidence.
  Semantic adjacency and custom protected paths are reviewed rather than advertised as automatic enforcement.
  → `CAP-DLV-delivery-workflows` worker inspection (MUST).
- A new task annotation and its reason are committed with the first source write. The typed list belongs to the
  single final or emergency worker envelope at turn end. Review checks annotation, task and AC before that record
  exists; Host validation and inspection subsequently enforce agreement. Rejected ranges retain existing recovery
  instead of discarding commits.
  → `CAP-DLV-delivery-workflows` worker result validation (MUST).
- This partially replaces `ADR-orchestration-workers` only for rejection of unlisted paths that satisfy recorded
  Tier B admission. Its remaining range, sync-output, worktree, Git and host-permission decisions remain in force.

## 5. Consequences

Routine adjacent-file misses can finish with a reviewable record. The generic workflow envelope gains an additive
field used by the SDD consumer. Reviewers still judge ownership and necessity, and a derived scope pass alone
cannot prove that a mutable task boundary was authorized. No sealed journal, project ownership registry or
configuration setting is added. Optional inspection in a cloud orchestrator remains that orchestrator's choice;
this decision promises only the shared shipped worker/reviewer contract.

## 6. Confirmation

- Envelope integration tests cover round trips, malformed inputs, kind restrictions and old records.
- Worker inspection tests cover valid, missing/mismatched, denied, explicit-scope and subsequent-turn cases.
- Boundary-parser tests retain existing values while exposing extension notes.
- Bundle content tests cover workers, reviewer guidance and Host validation.
- Semantic adjacency, test weakening and custom protected paths: Review only.
