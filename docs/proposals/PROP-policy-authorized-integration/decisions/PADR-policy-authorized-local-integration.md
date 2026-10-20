---
id: PADR-policy-authorized-local-integration
title: Policy authorizes local integration execution
summary: "Explicit dev-integration auto authorizes verified local merge and scoped cleanup through the existing MCP integration executor while preserving host permissions and separate publication authority."
proposal: PROP-policy-authorized-integration
status: draft
created_at: 2026-10-20
supersedes: ADR-integration-approval-asserted
---

# [PADR-policy-authorized-local-integration] Policy authorizes local integration execution

- **Status**: Draft
- **Supersedes on promotion**: `ADR-integration-approval-asserted`

## 1. Context & Problem Statement

`ADR-integration-approval-asserted` permits automatic gate passage but denies merge/deletion authority to every
policy value. Repeated business confirmations therefore remain necessary even when the repository opts into auto.
`PROP-policy-authorized-integration` requires that opt-in to authorize the complete verified local operation.

## 2. Decision Drivers

- One explicit shared setting supplies local gate and execution authority without repeated business confirmation.
- Preserve readiness, exact cleanup scope, state checks and host permissions.
- Reuse the existing executor and recovery contract; avoid a second integration engine or permission setting.
- Keep publication and cloud mutation outside local authority.

## 3. Considered Options

1. Existing MCP `integration_integrate` with policy dispatch in `IntegrationService` (selected): reuse request,
   locks, merge checks, scoped cleanup and process-local progress. Requires a connected and permitted MCP runtime.
2. Add executing CLI on the shared service: possible, but requires explicit owning-workspace/environment binding
   and restart recovery. Excluded from this implementation; current explicit manual CLI authority remains separate.
3. Change only the workflow gate or agent wording: insufficient because the current executor accepts ask only.

## 4. Decision Outcome

Subject to plan acceptance, shared `[workflow.approvals] dev-integration = "auto"` in the retained base checkout
will authorize verified local merge and exactly scoped worktree, selected local branch and extension cleanup.
The existing MCP service prepares and validates the request, grants `authority: policy` without calling the
confirmation callback, then uses its common execution engine. Ask remains the default and keeps native confirmation.
Neither caller declarations, local overlays, a source-only policy change nor tool-call permission grant authority.

All unrelated provisions of `ADR-integration-approval-asserted` remain: intent and direction decisions are human,
ask integration consent is asserted without an approval file, and reporting distinguishes policy from human consent.
This decision grants no new commit or publication authority. Auto PR execution is refused, required PR policy still
blocks local merge, and cloud remains read-only. No host sandbox, trust or tool policy is changed.

The immutable request binds policy and Git/cleanup identities. Preserve the current initial-call descendant-target
rule and stricter retained resume rule. Resume revalidates authority kind and effective policy, never widens scope
or repeats completed effects. Prospective auto-to-ask revocation refuses before the merge; external revocation stops
remaining work. After process loss, inspect and prepare a new request only for provable remaining scope; no approval
or journal file restores authority. Report cleanup whose evidence is lost as incomplete.

## 5. Consequences

Auto removes devkit business confirmation for eligible local integration. Actual unattended operation also requires
the host to permit the MCP tool and the server to have OS access; host refusal remains authoritative and cannot be
worked around by switching execution routes. Existing ask-mode tests and host evidence establish reusable pieces,
not implemented auto behavior. Development must verify the no-form transport path and actual merge/cleanup on both
Codex CLI and Claude Code, recording permission prompts separately. Without the MCP runtime, this implementation
provides no automatic CLI substitute. No extra settings, transport profile or durable recovery journal are added.
