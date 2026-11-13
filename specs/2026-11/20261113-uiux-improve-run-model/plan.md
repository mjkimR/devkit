---
id: PLAN-uiux-improve-run-model
spec: SPEC-uiux-improve-run-model
---

# Technical Plan: `SPEC-uiux-improve-run-model`

## 1. Constitution & Invariant Review

`ADR-uiux-task-approved-run` partially replaces unconditional consumer-workflow continuation in
`ADR-uiux-improvement-workflow-boundary` and `ADR-impeccable-session-authority`. Other authority and file-ownership
clauses remain. No new package, feature, layer, test tier or feature edge is introduced.

## 2. Architecture Overview & Impact

This is a content-only catalog change. The entry owns route selection, scope and Git boundaries; orchestration
applies that route to delegation and setup; the human README explains both paths. The capability and use case
restate the same contract. The promoted ADR and predecessor pointers already exist from handoff.

| Scenarios | Handling component | Evidence |
| --- | --- | --- |
| AC-01, AC-02 | Entry and route-choice section | Localized instruction assertions |
| AC-03, AC-08 | Entry, orchestration and guide | Existing authority/delegation/setup assertions updated for both routes |
| AC-04, AC-05 | Entry scope and delivery steps | Missing-authority and scope-boundary assertions |
| AC-06, AC-07 | Verification and completion instructions | Coverage, selected-workflow review and stale-document assertions |
| AC-09 | Installed consumer | Real isolated wheels, configured-approach and absent-record assertions |

No runtime API, CLI output, persisted state or migration changes. Existing user-operated interactive-command
routing is deliberately retained for the next approved proposal. Live trials remain best effort.

## 6. Verification & Test Plan

Run the focused catalog integration file and app-uiux-improve installed-consumer E2E, then `just lint-check`,
`just check`, `just test-affected --base fad216cee1ada8e31028d4bb97988692aa439238` preserving full fallback,
`devkit rules check --ci --base fad216cee1ada8e31028d4bb97988692aa439238`, envelope checks and sync checks.
Source-only changes require no frontend check. The initial sync check passed before edits. Sync after bundle edits
and record any tracked outputs. Medium independent code review and reconcile verification precede the final report.
