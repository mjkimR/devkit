---
id: PROP-worker-shared-state-mcp
title: MCP-owned shared state for workers across worktrees
summary: "Evaluate a local MCP service that owns shared worker coordination state across sandboxed worktrees. Define repository identity, ownership, authorization, durability and lifecycle while comparing bounded registry operations with a general shared workspace."
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-20
target_area: collaboration/
priority: medium                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/scope/
    - docs/capabilities/collaboration/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---


# [PROP-worker-shared-state-mcp] MCP-owned shared state for workers across worktrees

## 1. Background & Hypothesis

`SPEC-scope-registry-sandbox-access` retains Git storage and separates side-effect-free query/history access from
mutations. Register, update, release and recovery still need shared registry and per-worktree token writes.
`CAP-COLL-work-scope-registry` coordinates several workers against that state. Relocating it to one checkout's
`.devkit` does not make that path writable from every sandbox or eliminate ownership-token access.

A local MCP service could own shared filesystem operations and expose bounded coordination tools to workers.
The hypothesis is that a server-owned access boundary can reduce repeated path/permission provisioning across
worktrees. MCP does not itself grant filesystem access or authorize callers: the server's permissions, caller
identity, tool approvals and failure handling must be designed explicitly. Server-owned durable coordination
records and disposable worker scratch files have different lifecycles and must not be conflated.

This is a separate follow-up, not a dependency of the accepted read-access improvement. Keeping the direct CLI
with scoped approvals remains a valid baseline if service overhead exceeds the benefit.


The shared runtime and project registration foundation are owned by `SPEC-standalone-devkit-mcp`, which consumes
`SPEC-local-config-execution-environment`. This proposal owns coordination operations, authoritative storage,
concurrency and lifecycle. Prefer extending that runtime if the MCP option is selected; do not duplicate transport
extraction or registration work. Separate stdio processes still require an explicit shared-store design.

## 2. Technical Spike Questions

- **Q1 — Needed shared operations:** Which observed worker actions require shared mutation? Start with scope
  registration/update/release and ownership recovery; establish whether any additional shared artifact or scratch
  operation has a concrete consumer before adding a generic filesystem API.
- **Q2 — Service topology and discovery:** Compare an existing devkit MCP process with a dedicated local service.
  Multiple agent clients may launch separate MCP processes; how do they share one authoritative store and locking
  discipline? How are repositories, clones and linked worktrees discovered without trusting arbitrary paths?
- **Q3 — Authority and ownership:** Which caller may read, mutate, release or recover each record? How do scoped
  tool approvals map to operations, and how are owner tokens held without making a server a confused deputy?
  Define behavior for forged repository/worktree identities, cross-repository requests and denied authorization.
- **Q4 — Persistence and lifecycle:** Where does durable state live, who provisions access, and what survives
  process restart, client disconnect, worktree removal or base-checkout relocation? Define cleanup ownership,
  bounded retention and the difference between temporary artifacts and authoritative coordination records.
- **Q5 — Consistency and recovery:** Specify atomicity, concurrent clients, revisions, retry/idempotency and
  unknown outcomes. Decide whether CLI and MCP may coexist against one store and how fallback is made explicit.
- **Q6 — Cost and portability:** Compare setup, startup latency and maintenance across available hosts with the
  direct CLI baseline. Inspect `CAP-INT-mcp-services` for reusable host transport and authorization patterns while
  preserving package layering; integration approvals are not blanket authority for registry mutations.

## 3. Proposed Design & Impact

Planning should compare three bounded options: direct CLI with scoped path access, MCP wrappers around the
existing registry, and a service-owned registry with explicit client identity. A generic shared workspace is a
candidate only if evidence identifies consumers and contracts beyond the registry; otherwise defer it rather
than shipping arbitrary file operations. No transport, storage location or new public tool is selected yet.

Expected impact starts in `CAP-COLL-work-scope-registry` and its implementation. Planning must identify the actual
MCP owner/package, configuration changes and any additional code boundaries before Development. Existing
`shared_path`, namespace, token ownership and CLI result/error behavior must be accounted for explicitly.

Acceptance evidence for a selected design should include:

- Two workers in separate sandboxed worktrees observe each other's authorized updates; an unrelated repository
  remains isolated, even when its task names match.
- A denied or forged mutation changes nothing and reports a stable actionable result; a failed query is never
  presented as an empty registry. A server running with greater filesystem access does not widen caller authority.
- Concurrent update/release and retry after a lost response preserve ownership and revision semantics; process
  restart preserves required state and reports uncertain completion without blind destructive replay.
- Service absence, stale discovery and missing permissions produce explicit recovery instructions. No automatic
  fallback silently broadens permissions. Worktree deletion cannot remove another worker's live state.
- Setup steps, required grants, local call timings and recovery costs are compared with the baseline. Proposed
  temporary storage, if justified, has bounded retention and cannot delete authoritative records.

Non-goals: remote multi-host service, arbitrary file access, changing host-wide sandbox settings, universal approval
guarantees, replacing Git worktrees, and implementing this service as part of the query/history improvement.

## 4. Lifecycle & Retirement Criteria

This draft records the follow-up for later Planning; it neither accepts a server design nor starts implementation.
Medium Planning should produce an evidence-backed comparison, concrete tool/ownership boundaries and a recommended
Development effort. Accept a design only after its setup and authorization contract can be exercised locally.
Close with evidence if the direct CLI baseline remains preferable. Any generic shared workspace retained beyond
registry coordination needs an explicit consumer, lifecycle and verification scope before handoff.
