---
id: PLAN-uiux-improve-impeccable-routing
spec: SPEC-uiux-improve-impeccable-routing
---

# Technical Plan: `SPEC-uiux-improve-impeccable-routing`

## 1. Constitution & Invariant Review

`ADR-impeccable-question-relay` partially supersedes the fresh-child interactive-command restriction in
`ADR-impeccable-session-authority`. Native loading, explicit context-file permission, user-selected invocation and
coordinator acceptance remain. `ADR-uiux-task-approved-run` and its landed implementation retain route authority.
No architecture, dependency, package or runtime change is planned.

## 2. Architecture Overview & Impact

Update one catalog bundle's entry, orchestration reference and human guide. The entry routes selected Impeccable
work to the detailed contract; the reference owns capability checks, read-only question packets, confirmation,
continuation and fallbacks. Preserve all existing brief, source-attribution, permission and setup boundaries.

Reflect the same behavior in `CAP-DLV-uiux-improvement` rules 10 and 16 and
`UC-improve-an-interface-and-user-flow` extensions/examples. Finalize the promoted decision's current-state wording;
retain the predecessor ADR's exact partial-supersession pointer and all unrelated decisions.

## 3. Component & Interface Design

| Scenarios | Handling component |
| --- | --- |
| AC-01, AC-03 | Entry and orchestration: observe actual native load/continuation; report enablement and route to fallback |
| AC-02, AC-04, AC-05 | Orchestration: complete question packet, source-cited pre-fills, all-answer confirmation, same-child resume and new-round handling |
| AC-06, AC-07 | Existing brief and acceptance, with explicit read-only first phase and partial-execution return |
| AC-08 | Human guide, focused integration assertions and Living Spec reflection |

The packet is conversational data: question identifier, full question, suggested answer where useful and source
path/passage for a document-derived suggestion. No persisted schema or runtime API is introduced. A complete visible
packet can receive one explicit confirmation; omitted answers never imply confirmation. New relevant source facts
require affected-answer confirmation; lost continuation uses the user's session rather than a reconstructed child.

## 6. Verification & Test Plan

Run the focused catalog integration file, `just lint-check devkit-catalog`, `just check devkit-catalog`,
`just test-affected --base 49326e950da64ff92cc23bbd128d9e68d0bcec80 --tier all`, cumulative CI rules and sync checks.
The selector retains its full fallback and includes installed-consumer E2E. Review the existing negative and authority
assertions as well as new relay cases. Use one independent medium code-reviewer; self-check reconciliation only if
all exact targets agree and the effort exception applies. No live plugin/consumer trial is an acceptance gate.
