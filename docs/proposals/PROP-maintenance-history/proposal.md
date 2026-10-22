---
id: PROP-maintenance-history
title: Maintenance execution history on a GitHub orphan branch
summary: "Persists maintenance playbook execution records on a dedicated GitHub orphan branch through gh api, linked to the inspected source revision, without touching the local checkout or code history."
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-22
target_area: delivery/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: high                 # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-maintenance-operations
boundaries:
  owns:
    - packages/devkit-catalog/src/devkit_catalog/maintenance/
    - docs/capabilities/delivery/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-maintenance-history] Maintenance execution history on a GitHub orphan branch

## 1. Background & Hypothesis

Maintenance playbooks (`weekly-report`, `drift-reconciliation`, `review-refactor`) produce findings and decisions
that later runs and reports need, but nothing keeps them beyond the run. Recording each run on a dedicated GitHub
orphan branch through `gh api` keeps durable, revision-linked history apart from code history, without switching
branches, staging files, creating local commits or pushing. Manual playbook delivery does not depend on it. This
draft carries the scope its own milestone held before the
maintenance milestones merged into `MS-maintenance-operations`.

## 2. Technical Spike Questions

- **Q1**: Which GitHub Contents or Git Database endpoints give atomic multi-file publication and non-forced,
  retry-safe branch updates under concurrent writers?
- **Q2**: How does a run that inspected uncommitted changes identify that state, given a commit SHA alone does not?

## 3. Proposed Design & Impact

- A documented `gh api` procedure initializes a history branch (default `maintenance-history`) from a parentless
  root commit holding only history material; later records extend that branch, which is never merged into code
  branches. Existing branches are validated before use; unrelated history is never overwritten or force-updated.
- All three playbooks use one execution record: unique run ID, playbook and repository identity, start and finish
  timestamps with timezone, inspected source commit SHA captured at intake, review scope and outcome (completed,
  failed or interrupted). Source revisions and history commits stay distinct; records with applied changes link the
  resulting code commits. A run records whether its checkout held uncommitted changes and, when inspected, keeps the
  relevant diff or artifact reference.
- Records and reports are appended under playbook/run-specific paths, linking findings, verification, resolved and
  deferred items and follow-ups. A run with no findings stays distinguishable from a missing run; retrying the same
  run neither duplicates logical records nor silently replaces different content.
- Publication uses atomic commit creation when one run publishes several files, and leaves the local working tree,
  index, checked-out branch and local refs unchanged. Concurrent publications keep every successful record through
  non-forced updates and bounded retries. Authentication, permission, conflict, rate-limit and lost-response failures
  produce explicit publication outcomes and recovery actions, distinct from the run's own result.
- Records are listed and retrieved through `gh api`, filtered by playbook and inspected revision; an agent finds the
  latest completed run and its source revision without checking out or fetching the history branch. Durable history
  is not subject to the seven-day shared artifact TTL (`CAP-COLL-shared-artifacts`).
- Verification covers initialization, publication and retrieval per playbook, multi-file publication, no-finding and
  failed runs, duplicate retries, concurrent writers, publication failure recovery and unchanged local Git state.
  Destination and write authorization are explicit; output follows `ARCH-08-1-agent-output` and
  `CAP-ADV-agent-advisory-protocol`.
- Non-goals: scheduler or trigger design, the maintenance procedures themselves, records on the default code
  branch, merging the history branch, automatic code changes or integration, a general-purpose store and
  destructive history compaction or retention cleanup.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr maintenance-history "<title>" --summary "<Y-statement>" records a PADR in decisions/.
- On acceptance (plan-accept): devkit spec proposal accept maintenance-history --by user, then the Planning branch is merged.
  Development starts with devkit spec proposal handoff maintenance-history.
- On rejection: change only status: rejected, with the user's reason in the commit message.
-->
