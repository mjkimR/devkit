---
id: MS-maintenance-history
title: Maintenance execution history on a GitHub orphan branch
summary: "Persists maintenance playbook execution records and reports on a dedicated orphan branch through gh api, preserving source-revision traceability without changing the local checkout or code history."
status: planned
created_at: 2026-10-20
depends_on: [MS-reporting-and-actionable-insights, MS-drift-reconciliation, MS-refactoring-and-prevention-rules]
---

# [MS-maintenance-history] Maintenance execution history on a GitHub orphan branch

## Goal

Advances `ARCH-01-introduction-and-goals` §1.2 (Repository Governance & Deterministic Verification) and §1.3
(Delivery Workflow Orchestration) by providing durable, revision-linked execution history for the `maintenance`
bundle's `weekly-report`, `drift-reconciliation`, and `review-refactor` playbooks. Records are committed directly
to a dedicated GitHub orphan branch through `gh api`, keeping maintenance history separate from code history
without switching branches, staging files, creating local commits, or running a local Git push. This is a
follow-up to the three maintenance playbook milestones; their manual delivery does not depend on this history
backend or on scheduling.

## Exit condition

- A documented `gh api` procedure initializes a dedicated history branch, with `maintenance-history` as the
  default name, from a parentless root commit containing only history material. Subsequent records extend that
  branch's own history; the branch is not merged into code branches. Existing branches are validated before use
  and unrelated history is never overwritten or force-updated.
- All three playbooks use a common execution record with a unique run ID, playbook identity, repository identity,
  start and finish timestamps with timezone, inspected source commit SHA captured at intake, review scope, and
  outcome (completed, failed, or interrupted). Source revisions and history-storage commits remain distinct;
  records with applied changes also link the resulting code commits.
- A run records whether its inspected checkout contained uncommitted changes. When those changes are inspected,
  the record preserves the relevant diff or artifact reference; a commit SHA alone is not presented as identifying
  that inspected state.
- Completed records and reports are appended under playbook/run-specific paths, with links to findings,
  verification, resolved and deferred items, and follow-up work. A run with no findings remains distinguishable
  from a missing run. Retrying publication of the same run does not create duplicate logical records or silently
  replace different content.
- Record publication uses GitHub Contents or Git Database endpoints through `gh api`, including atomic commit
  creation when one run publishes several files. Verification demonstrates that the local working tree, index,
  checked-out branch, and local Git refs remain unchanged by publication.
- Concurrent publications preserve all successful records through non-forced branch updates and bounded retries.
  Authentication or permission failures, conflicts, API limits, and lost responses produce explicit publication
  outcomes and recovery actions. A publication failure remains distinct from the maintenance run's result.
- Records can be listed and retrieved through `gh api`, filtered by playbook and inspected revision, with links
  to the GitHub files and history commits. An agent can determine the latest completed run and its inspected
  source revision without checking out or fetching the history branch.
- Durable execution history and reports are not subject to the ephemeral artifact TTL proposed by
  `PROP-worker-shared-state-mcp`. Shared workspace artifacts may support work in progress, but expiring them does
  not remove the persisted record or its required evidence.
- Verification covers branch initialization, publication and retrieval for each playbook, multi-file publication,
  no-finding and failed runs, duplicate retries, concurrent writers, publication failure recovery, and unchanged
  local Git state. Destination and write authorization are explicit; agent-facing command output follows
  `ARCH-08-1-agent-output` and `CAP-ADV-agent-advisory-protocol`.

## Non-goals

- **Scope Excluded**: Scheduler or trigger design, implementation of the three maintenance procedures themselves,
  storing execution records on the default code branch, merging the history branch into code branches, automatic
  code changes or integration, replacing shared coordination state, a general-purpose database or artifact store,
  and destructive history compaction or retention cleanup.
