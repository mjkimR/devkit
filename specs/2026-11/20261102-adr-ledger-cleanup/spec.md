---
id: SPEC-adr-ledger-cleanup
title: Topic compaction groups and retired stale ADR clauses
summary: ADR compaction groups follow topics instead of the whole supersession closure, with cross-group partial supersession recorded on the replacements; a retiring ADR removes the native-approval and moved-ownership clauses that no longer hold.
status: completed
created: 2026-11-02
related_capabilities: [CAP-DOCS-document-model]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-adr-ledger-cleanup] Topic compaction groups and retired stale ADR clauses

## 1. Problem Statement & Motivation

The 2026-11-02 ADR compaction left 15 ADRs uncompacted, for two reasons:

- `ADR-decision-ledger` closes every compaction group under supersession. Two bridging supersessions join 13
  integration ADRs into one component, and one replacement of it would be a mega-ADR
  (`FB-integration-adr-chain-uncompacted`).
- `ADR-proposal-acceptance` and `ADR-mcp-runtime-and-shared-artifacts` still state the removed native approval route
  (`FB-native-approval-adrs-without-pointers`).

The compaction also found `ADR-document-system` and `ADR-steering-documents` still stating owners that later
decisions moved (`FB-adr-ownership-moves-without-pointers`).

## 2. User Stories

- **US-1**: As a maintainer compacting ADRs, I want groups formed by topic, so that a bridging supersession does not
  force unrelated decisions into one record.
- **US-2**: As an agent checking a design against ADRs, I want no accepted clause to state a removed route or a
  moved owner.

## 3. Non-Goals

1. **Scope Excluded**: Compacting the integration ADRs. That is a separate `adr-compaction` run under the new rule.
2. **Scope Excluded**: Any behavior or code change.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Topic grouping replaces the closure rule
- **Given** `ADR-decision-ledger` (Compaction)
- **When** the change lands
- **Then** `ADR-group-compaction-by-topic` (accepted) supersedes its closure sentence only, with the pointer lines
- **And** `CAP-DOCS-document-model` §Decision supersession states the grouping rules with RFC 2119 keywords:
  - groups are formed by topic;
  - a wholly superseded ADR joins its superseder's group;
  - when a partial supersession crosses groups, the target's replacement leaves out the replaced clauses and the
    superseding replacement cites the target's replacement;
  - a kept ADR's `supersedes` is renamed to the replacement, which gains the matching pointer.
- **And** the `adr-compaction` playbook applies these rules in Steps 1 to 3, and a guidance test asserts them

### [AC-02] Stale clauses are retired
- **Given** the native-approval clauses of `ADR-proposal-acceptance` and `ADR-mcp-runtime-and-shared-artifacts`
- **And** the moved-ownership clauses of `ADR-document-system` and `ADR-steering-documents`
- **When** the change lands
- **Then** `ADR-retire-native-approval-and-moved-ownership-clauses` (accepted) supersedes exactly those clauses, and
  names the decision that holds the current rule
- **And** each target stays `accepted` and carries a "Superseded in part by" line under its heading and at each
  affected statement

### [AC-03] Source feedback and checks
- **Given** the change
- **When** it lands
- **Then** `FB-native-approval-adrs-without-pointers` and `FB-adr-ownership-moves-without-pointers` are `resolved`
- **And** `FB-integration-adr-chain-uncompacted` stays `open` until the compaction run
- **And** `uv run devkit rules check` and `just test-affected` exit `0`

## 5. Source feedback

- `FB-native-approval-adrs-without-pointers`, `FB-adr-ownership-moves-without-pointers`: direct fixes.
- `FB-integration-adr-chain-uncompacted`: enabled here, resolved by the following compaction run.
