---
id: SPEC-retire-stale-integration-clauses
title: Retire stale integration ADR clauses
summary: A new ADR retires the pre-confirmation --auto/--admin refusal clause and the MCP approval-form text rules that the Host-run CLI integration no longer has; FB-bundle-text-bare-devkit-commands is dismissed.
status: in-progress
created: 2026-11-02
related_capabilities: [CAP-INT-mcp-services]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-retire-stale-integration-clauses] Retire stale integration ADR clauses

## 1. Problem Statement & Motivation

Integration moved from MCP-native confirmation to Host-run CLI calls (`ADR-host-cli-lifecycle-authority`). Commits
`2a491881` and `8f570521` then removed the MCP-native approval paths and the MCP confirmation channel. Two accepted
ADRs still state clauses that only that channel could carry out:

- `ADR-local-and-pull-request-integration` says a path that would need `--auto` or `--admin` is refused before the
  confirmation. The PR route reaches these cases only after approval:
  - pending checks return `INTEGRATION_CHECKS_PENDING`;
  - a merge only an admin could make ends as `INTEGRATION_MERGE_REFUSED`;
  - unreadable classic protection is disclosed, not refused.
- `ADR-configuration-language-and-rendering` sets approval-form text rules, for example "explain all choices even when
  a host omits schema metadata", "sample language once per form" and "display provider prose verbatim". It also keeps
  "native approval routes" in local text. No such form exists any more.

`SPEC-adr-normative-outcomes` left these clauses unmarked and handed them off as `FB-pr-auto-admin-refusal-point` and
`FB-stale-approval-form-clause`.

## 2. User Stories

- **US-1**: As an agent checking a design against accepted ADRs, I want no accepted clause to describe an approval
  channel or refusal point that does not exist, so that I do not build or review against a contract the code cannot
  meet.

## 3. Non-Goals

1. **Scope Excluded**: Changing integration code. The current refusal points stay as they are.
2. **Scope Excluded**: Changing the domain-owned English and Korean copy, `presentation.language` resolution, or
   `CAP-DIST-sync-and-transactions`.
3. **Scope Excluded**: Rewriting bundle prose that names bare `devkit` commands.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] A new ADR retires the stale clauses
- **Given** the two ADRs named in §1
- **When** the change lands
- **Then** `ADR-retire-stale-integration-approval-clauses` is `accepted` and lists both ADRs in `supersedes`
- **And** its Decision Outcome names each replaced clause, and states the current behavior that replaces it with the
  ID of the capability that states it
- **And** both earlier ADRs stay `accepted`, each with a "Superseded in part by" line under its heading and at each
  affected statement

### [AC-02] Still-valid parts stay in force
- **Given** the retired clauses
- **When** a reader looks for the remaining contract
- **Then** these parts stay in force: domain-owned static English and Korean copy, preserved canonical keys, action
  values, identifiers and evidence, and MCP-first discovery in local text
- **And** these parts are not retired: the fork and merge-queue refusals before the confirmation, and the ban on
  enqueue, auto-merge and admin-merge (`CAP-INT-mcp-services`)

### [AC-03] Source feedback is closed
- **Given** `FB-pr-auto-admin-refusal-point`, `FB-stale-approval-form-clause` and `FB-bundle-text-bare-devkit-commands`
- **When** the change lands
- **Then** the first two are `resolved`, with a Disposition naming this spec
- **And** the third is `dismissed`, with a Disposition giving the user's reason
- **And** `uv run devkit rules check` and `just test-affected` exit `0`

## 5. Source feedback

- `FB-pr-auto-admin-refusal-point`: direct fix (retire the ADR clause).
- `FB-stale-approval-form-clause`: direct fix (retire the ADR clauses).
- `FB-bundle-text-bare-devkit-commands`: dismissal decided by the user. `CAP-DIST-context-and-playbooks` scopes the
  `uv run devkit` rule to output-suggested invocations, and the spec bundle's constitution translates bundle prose.

## 6. Assumptions

- The user chose to retire both clauses through one ADR, to keep the code unchanged and to dismiss the bare-command
  feedback (conversation, 2026-11-02).
- "Source/provider prose is displayed verbatim" served only the MCP confirmation forms, so it is retired with them.
