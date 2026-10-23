---
id: ADR-host-cli-lifecycle-authority
title: Conversational Host authorization for CLI lifecycle execution
summary: For Host lifecycle execution in local shells, we accept conversational ask decisions and let CLI revalidate scope without an approval credential, to remove the mandatory MCP path, accepting that devkit cannot authenticate the user's conversational decision.
proposal: SPEC-cli-host-lifecycle
status: accepted
created_at: 2026-10-23
supersedes:
  - ADR-delivery-decision-boundaries
  - ADR-local-and-pull-request-integration
---

# [ADR-host-cli-lifecycle-authority] Conversational Host authorization for CLI lifecycle execution

- **Status**: Accepted
- **Date**: 2026-10-23

---

## 1. Context & Problem Statement

Proposal acceptance, handoff and integration execution currently depend on lifecycle MCP tools. Under `ask`, those tools request native confirmation and bind the answer to a retained operation. The CLI exposes proposal state changes and worktree finish, but it does not expose the same composed checks and effects. A Host without lifecycle MCP cannot complete these operations through devkit's CLI alone.

The proposed operating model assigns these effects to the Host, which can present the exact scope in conversation and then invoke the CLI. The CLI can revalidate source, report, policy, readiness and cleanup identity before mutation, but it cannot authenticate a conversational answer. Host filesystem permission remains a separate control and does not establish business approval.

## 2. Decision Drivers

- A Host must complete the scoped lifecycle when lifecycle MCP is unavailable.
- `ask` and `auto` retain separate, explicit authority rules.
- Execution revalidates source, report, policy, readiness and cleanup scope immediately before mutation.
- Local merge, pull-request policy, required checks and publication limits remain effective.
- Partial results identify completed effects and the failing step without creating a durable recovery service.
- Shared artifact access and proposal report publication retain their existing boundaries.

## 3. Considered Options

### Keep native lifecycle confirmation as the only `ask` execution path

This keeps the current approval binding and process-local recovery model. It requires a connected MCP service for acceptance, handoff and integration, so it does not meet the proposal's Host CLI requirement.

### Let the Host obtain conversational approval and execute through CLI (selected in `answer-01`)

This removes the lifecycle MCP requirement and uses host instructions to present the exact scope before execution. The CLI revalidates the operation but does not authenticate the conversational decision. This makes the Host responsible for carrying the user's answer correctly.

### Persist a CLI approval credential or recovery journal

This could bind a later command to an earlier decision, but it introduces durable authorization and recovery state that the proposal excludes. It also creates a second approval runtime.

## 4. Decision Outcome

Under `ask`, the Host obtains the user's conversational decision after presenting the exact execution scope, then invokes the CLI. The CLI revalidates scope but accepts no approval token or proof of user identity. The user selected this option in `answer-01` because the Host owns lifecycle execution and the CLI path must work without lifecycle MCP. The plan-accept command records acceptance separately.

Under `auto`, the CLI reads effective policy from the retained base and applies the same readiness and identity checks. Caller arguments, local overlays and host command permission do not grant policy authority. Pull-request policy and remote publication limits remain unchanged.

The CLI returns completed effects, the failed step and stable actionable errors. It stores no approval session or recovery journal. After an unknown result, the Host inspects Git, worktree and PR state, then invokes only the remaining operation whose scope can be revalidated.

## 5. Consequences

- The Host can complete accepted lifecycle operations without lifecycle MCP registration.
- An agent can invoke a CLI command after an incorrect interpretation of conversation; the CLI cannot detect that mistake. The Host must show the operation and exact scope before asking.
- A process restart loses in-memory execution progress. Recovery depends on observable Git, worktree, proposal and PR state.
- Development must preserve independent `plan-accept`, `proposal-handoff` and `dev-integration` policy boundaries.

## 6. Confirmation

Development verifies that `ask` requires the Host instruction path and that CLI arguments cannot claim approval; `auto` derives authority only from the retained base policy. Integration tests cover stale source/report, changed policy, readiness refusal, local and pull-request policy, and post-merge cleanup recovery. Review confirms the conflicting native-confirmation clauses in `ADR-delivery-decision-boundaries` and `ADR-local-and-pull-request-integration` are superseded while their unrelated decision boundaries remain. `ADR-mcp-runtime-and-shared-artifacts` remains in force for shared storage and report publication.
