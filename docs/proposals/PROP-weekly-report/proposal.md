---
id: PROP-weekly-report
title: Evidence-based weekly maintenance reporting
summary: Define a manually invoked weekly-report playbook that turns revision-bound repository evidence into a report and prioritized follow-ups while separating generation from authorized publication.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-21
target_area: capabilities/delivery/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-reporting-and-actionable-insights
boundaries:
  owns:
    - packages/devkit-catalog/
    - guides/
    - docs/capabilities/delivery/
    - docs/capabilities/distribution/
    - docs/stories/governance/
  excludes:
    - packages/devkit/src/devkit/integration/
    - packages/devkit-dist/src/devkit/shared/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-weekly-report] Evidence-based weekly maintenance reporting

## 1. Background & Hypothesis

`MS-reporting-and-actionable-insights` calls for a manually invoked report that makes completed work, decisions,
repository health and next actions inspectable. The maintenance bundle introduced by `PROP-periodic-drift-reconciliation`
is the delivery home. A reporting procedure can consume available evidence without running drift or refactoring
first, and without a scheduler or history backend.

## 2. Technical Spike Questions

- Which existing Git, document lookup and governance outputs establish completion, integration, ADR changes and
  unresolved work without treating proposal acceptance or a commit alone as feature completion?
- How are observation interval, timezone, inspected revision and dirty state captured, and how are missing,
  stale and non-comparable prior reports represented?
- What report structure and rerun identity permit prioritized follow-ups without duplicating existing feedback?
- How can generation yield a useful local artifact when publication destination or authorization is absent,
  while an explicitly authorized publication records its independent outcome?

## 3. Proposed Design & Impact

Deliver `weekly-report` as an independent content-only playbook in `maintenance`, extend the implicit `all`
preset and introduce `reporting` for this asset. Preserve `upkeep` and explicit-invocation rules. Reuse existing
commands and evidence; do not introduce an analytics runtime. Planning should define intake, evidence collection,
report sections, confidence/limitations, follow-up deduplication, publication and completion evidence.

Candidate acceptance evidence:

- Given a selected interval/timezone and repository revision, a manual run produces a report linking completed
  work, ADR changes, behavior changes and unresolved items to source evidence.
- Given absent drift/refactoring results, the report identifies missing evidence without claiming a clean result
  and without invoking those procedures automatically.
- Given existing feedback or proposals, recommendations cite those destinations instead of duplicating them.
- Given absent publication configuration or authority, generation succeeds with publication explicitly pending;
  a separately authorized publication and its failure are distinguishable from report generation.
- Given a rerun for the same interval, the selected identity/replacement policy is explicit and verified.
- Package discovery, preset selection, recommendation guidance and consumer smoke cover the new asset.

Non-goals: scheduler implementation, external analytics, automatic source fixes, mandatory maintenance sweeps,
GitHub history storage (`MS-maintenance-history`), and publication without authorization. The initial report is
not stored as a seven-day proposal-review artifact.

## 4. Lifecycle & Retirement Criteria

Feature / proposal depth. Planning effort is medium for the report and publication boundary decisions, with an
independent challenger; recommended Development effort is medium. Development depends on the maintenance bundle
landing, while Planning can inspect its committed worktree evidence. Acceptance and Development start remain
separate decisions. No milestone state transition is included.
