---
id: PLAN-weekly-report
spec: SPEC-weekly-report
---

# Technical Plan: `SPEC-weekly-report`

## 1. Constitution & Invariant Review

None. `ADR-weekly-report-evidence-and-publication` supplies the accepted decision; the existing
`CAP-DIST-context-and-playbooks` exact retrieval and manual invocation contract needs no runtime change.

## 2. Architecture Overview & Impact

Extend the existing content-only catalog maintenance bundle with one weekly-report Markdown playbook and a
reporting preset. Preserve drift-reconciliation/upkeep and implicit all. Update catalog selection/discovery tests,
README and bundle recommendations. Reconcile reporting into a new delivery capability and governance story,
and update the content-packages inventory. No dependencies, scheduler, connector or runtime code is added.

## 3. Component & Interface Design

The playbook follows intake, evidence collection, assessment, immutable local generation and independently
authorized publication. Use existing commands; no new API or sentinel. Its report outline and companion outcome
record make identities, citations, limitations, retry decisions and publication receipts inspectable.
Use a run-specific filename and exclusive creation; publication state changes only the companion record.
This avoids overwriting earlier evidence and avoids changing bytes after publication.

## 4. Failure Modes

Missing optional evidence yields explicit gaps. Missing identity, interval, or verified writable artifact fails
generation. Missing publication authority stays pending. Lost response stays unknown until destination evidence
resolves it; no blind retry. Source-state changes invalidate affected observations rather than mixing snapshots.

## 5. Verification & Test Plan

Catalog tests cover opt-in discovery, reporting/upkeep/all deployment, valid headers and exact retrieval.
Run catalog lint/type/tests, just test-affected preserving full fallback, consumer smoke and cumulative rules.
Record manual scenarios in this unit's materials: bounded report with delivery/decision/action citations;
missing/stale/failed and incompatible sources; dirty/changing revisions; half-open/DST intervals; preserved
same-period rerun; pending, verified controlled-fixture publication, failed and unknown outcomes. Use isolated
local fixtures only, no external publication and no generic publisher harness. Review at medium effort with
independent code-reviewer and reconcile-reviewer. All source-feedback direct fixes are absent; preserve the
Host's unrelated pilot observation unchanged.
