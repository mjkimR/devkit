---
id: FB-review-refactor-contract-removal-skips-adr-check
title: A review-refactor contract removal reached Development without the accepted ADRs it contradicts
scope: repo
kind: change-request
category: missing-capability
target: packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/review-refactor/references/applying.md
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-11-11
---

# [FB-review-refactor-contract-removal-skips-adr-check] A review-refactor contract removal reached Development without the accepted ADRs it contradicts

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `applying.md` §8 routes each approved removal of a command, option or public interface as
  its own work item through the normal development workflow, "with the contract and documentation updated". The
  decision round does not ask which accepted decisions state the removed behavior.
- **Proposed Procedure**: In the decision round for a contract removal, list the accepted decision records and
  capability or architecture contracts that state the behavior. Put the needed decision change (a superseding
  decision or a supersession pointer) and those documents into the work item's agreed intent and write scope.
- **Expected Benefit**: The development worker no longer stops with needs_input, and no recovery turn is needed to
  widen the scope.
- **Cost & Risk**: A document search per contract removal during the decision round.
- **Attempted**: Tested in this session, after the fact. The recovery turn wrote the ADR and widened the scope, and
  the unit then completed.

## Diagnostic Details

- **Reproduction**: Approved removal AO-01 (retire `worktree finish --merge`) became spec unit `retire-finish-merge`
  with a code-and-docs scope only.
- **Expected / Actual**: Expected one Development turn. Actually, worker-01 stopped needs_input. Four accepted ADRs
  stated the finish-merge landing route, and the agreed scope did not admit an ADR or the workflow guard module.
- **Versions**: worker-01 head fdf531d8; landed as fb2c9fbe.
- **Conditions**: Four contract removals were started in parallel from one run report.
- **Workarounds Attempted**: The user chose to retire the guard group and extend the scope. A recovery worker wrote
  `ADR-single-local-landing-route` with pointers in the four ADRs. This worked.
- **Related Assets**: review-refactor `references/applying.md` §8; `ADR-single-local-landing-route`.

## Evidence

```text
worker-01: status=needs_input — removal contradicts ADR-local-and-pull-request-integration, ADR-orchestration-workers,
ADR-worktrees-and-scope, ADR-package-ownership-and-release-version; ADR and workflow/usecases/integration.py outside scope
recovery: resolution-01 + new ADR, unit completed, integrated fb2c9fbe
```

- **Disposition**: review-refactor references/applying.md §8 now lists the accepted decisions and contracts stating a removed behavior before approval and puts the decision change and documents into the work item's intent and scope.
