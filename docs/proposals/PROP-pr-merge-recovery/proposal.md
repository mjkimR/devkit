---
id: PROP-pr-merge-recovery
title: Recover uncertain pull request merge outcomes across CLI calls
summary: Define how integration identifies prior pull request merge attempts and resumes safely after unknown outcomes or closed pending requests.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-28
target_area: capabilities/integration/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: high                      # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit/src/devkit_agt/features/integration/
    - docs/capabilities/integration/
  excludes:
    - packages/devkit-mcp/
task_kind: bugfix                     # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-pr-merge-recovery] Recover uncertain pull request merge outcomes across CLI calls

## 1. Background & Hypothesis

A fresh integration invocation can issue another merge after an unknown PR merge outcome, and a closed pending PR is not retained as a refusal. Existing evidence used a fake GitHub provider.

## 2. Technical Spike Questions

- **Q1**: How should a fresh invocation identify an earlier uncertain merge attempt without treating stored state as authority?
- **Q2**: Can remote state alone support safe refusal or recovery, or is a bounded local journal needed?
- **Q3**: How should a closed unmerged pending PR be distinguished from a new integration request?

## 3. Proposed Design & Impact

Compare refusal, remote observation and bounded persistent recovery state against CAP-INT-mcp-services. Preserve fresh Host authority, source identity and remaining-effect validation. Any change to the no-persistent-journal contract needs a PADR. Use fake providers for Planning; no remote writes are authorized.

## 4. Lifecycle & Retirement Criteria

Define deterministic unknown/open/merged/closed outcomes and prove that retry never blindly issues a second merge. State storage invalidation and authority limits if persistence is selected.

## Source feedback

- `FB-integration-reissues-merge-after-unknown-outcome`: resolve the recorded problem through this proposal; no implementation is authorized before plan acceptance and handoff.
