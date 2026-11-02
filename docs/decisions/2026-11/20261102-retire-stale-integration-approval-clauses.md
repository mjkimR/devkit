---
id: ADR-retire-stale-integration-approval-clauses
title: Retire integration approval clauses the CLI route no longer carries
summary: "For ADR clauses written for the removed MCP confirmation channel, we retire the pre-confirmation --auto/--admin refusal and the approval-form text rules, to keep accepted ADRs in step with Host-run CLI integration, accepting that an admin-only merge is refused at the merge call."
status: accepted
created_at: 2026-11-02
supersedes: [ADR-local-and-pull-request-integration, ADR-configuration-language-and-rendering]
---

# [ADR-retire-stale-integration-approval-clauses] Retire integration approval clauses the CLI route no longer carries

- **Status**: Accepted
- **Date**: 2026-11-02
- **Deciders**: user, agent
- **Involved Components/Capabilities**: `CAP-INT-mcp-services`, `CAP-DIST-sync-and-transactions`,
  `CAP-DIST-content-packages`

---

## 1. Context & Problem Statement

`ADR-host-cli-lifecycle-authority` moved integration approval to the Host's conversation, followed by a CLI call.
Commits `2a491881` and `8f570521` then removed the MCP-native approval paths and the MCP confirmation channel. Two
accepted ADRs still state clauses that only that channel could carry out:

- `ADR-local-and-pull-request-integration` refuses "any path that would need `--auto` or `--admin`" before the
  confirmation. The PR route reaches these cases only after approval:
  - pending checks return `INTEGRATION_CHECKS_PENDING`;
  - a merge that only an admin could make ends as `INTEGRATION_MERGE_REFUSED` at the merge call;
  - unreadable classic protection is disclosed, not refused.
- `ADR-configuration-language-and-rendering` sets rules for confirmation forms. Messages explain every choice when a
  host omits schema metadata, provider prose is shown verbatim, and language is sampled once per form. It also keeps
  "native approval routes" in local text. No such form or route exists.

---

## 2. Decision Drivers

- Accepted ADRs agree with the shipped integration route.
- Unsafe merges stay impossible: devkit never enqueues, auto-merges or admin-merges.
- No new code is written to honor a clause whose channel is gone.

---

## 3. Considered Options

### Option 1: Retire the clauses (Selected)
- **Overview**: Replace the stale clauses. The current behavior, already stated in `CAP-INT-mcp-services`, stands.
- **Pros**: No code change; ADRs match the route.
- **Cons**: An admin-only merge costs one approval before it is refused.

### Option 2: Move the `--auto`/`--admin` refusal into `prepare`
- **Overview**: Detect admin-only and auto-merge paths before the approval.
- **Pros**: Matches the original wording.
- **Cons**: Classic branch protection is not always readable, so `prepare` cannot decide every case, and the approval
  it would save is cheap.

---

## 4. Decision Outcome

We adopt **Option 1**. This ADR replaces only the clauses below. Every other clause of the two ADRs stays in force,
and both ADRs stay `accepted`.

- From `ADR-local-and-pull-request-integration`, it retires the refusal before the confirmation of "any path that
  would need `--auto` or `--admin`".
- The PR route MUST NOT enqueue, auto-merge or admin-merge. A merge that needs admin rights ends as
  `INTEGRATION_MERGE_REFUSED`. → `CAP-INT-mcp-services`
- The refusals before the confirmation for an unresolvable remote, missing or unauthenticated `gh`, a fork PR and a
  merge queue stay in force.
- From `ADR-configuration-language-and-rendering`, it retires these confirmation-form rules: messages explain every
  choice when a host omits schema metadata, source and provider prose is displayed verbatim, and language is sampled
  once per form.
- It also retires "native approval routes" from the local-text clause. Local text keeps MCP-first discovery and
  connection.
- Domain-owned static English and Korean copy and the preserved canonical keys, action values, identifiers and
  evidence stay in force. `CAP-DIST-sync-and-transactions` and `CAP-DLV-proposal-planning` state them.

---

## 5. Consequences

- **Positive**: No accepted ADR describes a refusal point or form that the code does not have.
- **Negative / Risks**: A user can approve an integration that then ends as `INTEGRATION_MERGE_REFUSED`.
- **Follow-ups**: None.

---

## 6. Confirmation

- `CAP-INT-mcp-services` §Authority and route limits.
- `rg "ctx.elicit|elicit\(" packages/` finds no confirmation form.
