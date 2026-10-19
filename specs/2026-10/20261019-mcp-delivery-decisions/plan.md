---
id: PLAN-mcp-delivery-decisions
spec: SPEC-mcp-delivery-decisions
---

# Technical Plan: `SPEC-mcp-delivery-decisions`

## Invariant review

Preserve `CAP-INT-mcp-services`, layer boundaries and the read-only viewer. SDD supplies presentation evidence; integration renders it without importing SDD models. Existing task and cleanup authority checks remain mandatory.

## Components

AutoHub: add a shared activity preview read model/API/MCP tool. Read the proposal at an immutable Git SHA. The web confirmation dialog and a new native MCP handoff tool consume that same preview. Add expected_base_sha to start requests and validate before any branch mutation. Existing direct start tools remain available for agents already authorized to start; the handoff tool obtains native user approval.

Devkit: add title/summary as deterministic provider evidence from the committed anchor, and render readable merge intent before exact scope. No new dependency or schema migration.

## Failures

Native confirmation failure grants no authority. Decline/cancel returns an explicit non-started result. Stale base requires a fresh review. Request recovery preserves existing branch/PR enrollment semantics; this change does not claim a global exactly-once transaction.

## Verification

Unit tests cover preview defaults, overrides, stale starts and non-approval. Frontend tests cover summary and per-activity confirmation; run AutoHub lint/type/build checks. Run devkit lint/type checks and just test-affected, including existing real MCP/Git confirmation tests. Independent medium code and reconcile review cover both worktrees.
