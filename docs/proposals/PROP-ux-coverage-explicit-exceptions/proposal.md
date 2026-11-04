---
id: PROP-ux-coverage-explicit-exceptions
title: Recognize explicit global and off-screen UX coverage exceptions
summary: "Recognize reasoned global-control and off-screen exceptions in UX coverage without weakening missing-reference warnings or contradictory-link errors."
status: reviewing
created_at: 2026-11-04
target_area: capabilities/governance/
priority: medium
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-docs/src/devkit_docs/features/governance/usecases/
    - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/ux_coverage/
    - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/
    - docs/capabilities/governance/
  excludes:
    - packages/devkit-docs/src/devkit_docs/features/governance/usecases/ux_links.py
    - .devkit/managed/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-ux-coverage-explicit-exceptions] Recognize explicit global and off-screen UX coverage exceptions

## 1. Background & Hypothesis

UX writing permits a global control to omit its use-case Step and an off-screen use-case step to omit a screen citation. RULE-ux-coverage still warns for each omission, including intentionally unlinked controls and background work. Its guide provides no per-item exception mechanism. Repeated expected warnings compete with genuine missing links and encourage invented references merely to make a check quiet.

Consumer evidence: resource-indexer at commit `09f1a8df0dffcf047da5efe2305dd3f6c7fc1058` reported 40 coverage warnings: 27 uncited use-case steps and 13 interactions without Step cells. Those are candidates for review, not 40 confirmed documentation defects. The navigation document intentionally leaves theme switching, skip-to-content and small-screen menu controls unlinked. The installed coverage tests also expect an off-screen mail-sending step to warn. These examples reproduce the mismatch between allowed writing and persistent warnings.

Hypothesis: narrowly scoped, explicit classifications with a substantive reason can recognize legitimate exceptions while preserving useful traceability checks. The owner can review the reason alongside the action; broad suppression and inferred exceptions are unnecessary for this personal-tool threat model.

## 2. Technical Spike Questions

- **Q1**: What is the smallest per-interaction and per-use-case-step notation that records a global or off-screen exception plus its reason without adding boilerplate to ordinary linked steps? Compare a structured local marker with a small document-level declaration keyed to existing steps/rows; prefer the notation that survives edits and is easiest for agents to validate.
- **Q2**: How will malformed declarations, removed step keys and declarations attached to already linked items be diagnosed without silently disabling coverage? Existing documents without declarations must retain their current warnings.
- **Q3**: Can findings point directly to the uncited use-case step rather than the first referencing UX document, so a navigation panel does not appear to own unrelated workflow gaps? Keep this diagnostic adjustment within the same coverage rule if selected during Planning.

## 3. Proposed Design & Impact

Retain the current distinction: missing coverage is a warning, contradictory links remain errors under RULE-ux-links. Add an explicit, reasoned way to classify only a particular interaction as global or a particular use-case step as off screen. Blank cells and uncited steps alone must not imply an exception. The classification must not bypass unknown IDs, invalid step references, reverse-link contradictions or reachability checks.

Keep the rule, its tests, writing instruction and guide aligned. Select the exact notation during Planning; no consumer should need a repository-wide disable or a severity downgrade. This proposal does not implement the rule or change consumer repositories.

Expected affected contracts: CAP-GOV-spec-rules and ADR-ux-screens; inspect their references during Planning. Preserve the accepted decision unless Planning identifies a semantic change requiring a new ADR. Changes stay in devkit-docs and its owned bundle assets.

### Acceptance examples for Development

1. A theme toggle or skip-to-content interaction explicitly classified as global with a reason produces no missing-Step warning; an unclassified blank row still warns.
2. A genuine background-only step explicitly classified as off screen with a reason produces no missing-screen warning; an unclassified uncited step still warns.
3. An unknown, malformed or stale declaration is diagnosed and cannot hide a missing-coverage finding.
4. A contradictory or nonexistent explicit UX/use-case link still fails its existing validation even when a coverage exception is present.
5. Existing documents and severity settings retain their behavior until an explicit classification is added. No heuristic based on label words such as "theme" or "background" is used.
6. Focused rule tests cover both accepted exceptions and negative controls; published writing instructions demonstrate one valid example of each retained classification.

## 4. Lifecycle & Retirement Criteria

Retain this as a Backlog draft. Planning settles the notation and validation contract, then ordinary acceptance and handoff create one feature spec. Completion requires maintained regression tests, synchronized guidance and a consumer example showing that genuine missing links remain visible while explicitly classified exceptions stop recurring.

Non-goals: implementing this proposal now, making every coverage warning blocking, disabling coverage globally, weakening contradictory-link errors, adding runtime UI features or manufacturing use cases for global controls. Consumer documentation maintenance can proceed under existing rules; it does not depend on this draft being implemented.
