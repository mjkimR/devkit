---
id: PLAN-mcp-delivery-decisions
spec: SPEC-mcp-delivery-decisions
---

# Technical Plan: `SPEC-mcp-delivery-decisions`

## Invariant review

Preserve `CAP-INT-mcp-services`, layer boundaries and the read-only viewer. SDD supplies presentation evidence; integration renders it without importing SDD models. Existing task and cleanup authority checks remain mandatory.

## Components

devkit-spec: register a spec_handoff service with the existing devkit.host.services extension point. Read the accepted proposal, expose its summary and plan with effort defaulted from dev_effort, then obtain native form approval before creating the Development worktree and running the existing handoff library. Revalidate base HEAD, clean state and policy before creation and source HEAD before handoff. Return the selected effort as run input; retain partial worktrees for explicit recovery. AutoHub is an alternative host and is outside this change.

Devkit: add title/summary as deterministic provider evidence from the committed anchor, and render readable merge intent before exact scope. No new dependency or schema migration.

## Failures

Native confirmation failure grants no authority. Decline/cancel returns an explicit non-started result. Stale base requires a fresh review. Request recovery preserves existing branch/PR enrollment semantics; this change does not claim a global exactly-once transaction.

## Verification

Unit tests cover preview defaults, overrides, stale starts and non-approval. SDK transport tests cover the actual native form exchange. Run devkit lint/type checks and just test-affected, including existing real MCP/Git confirmation tests. Independent medium code and reconcile review cover both worktrees.
