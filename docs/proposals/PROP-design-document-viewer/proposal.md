---
id: PROP-design-document-viewer
title: Minimal documentation-layer navigation in the repository viewer
summary: "Validates existing viewer navigation for the chosen domain, design and operations representations and adds only functionality required by demonstrated gaps."
status: draft
created_at: 2026-11-16
target_area: viewer/
priority: high
size: L
planning_effort: medium
dev_effort: medium
milestone: MS-documentation-system-evolution
boundaries:
  owns:
  - packages/devkit-viewer/
  - docs/capabilities/viewer/
  - docs/usecases/
  - docs/ux/
  - docs/architecture/
  - docs/decisions/
  - docs/development/reference/
  - docs/proposals/PROP-design-document-viewer/
  excludes:
  - packages/devkit-docs/src/devkit_docs/bundles/
  - packages/devkit-spec/
task_kind: feature
workflow: sdd-proposal
depends_on:
- PROP-design-document-foundation
- PROP-domain-model-documents
- PROP-operations-documents
---

# [PROP-design-document-viewer] Minimal documentation-layer navigation in the repository viewer

## 1. Background & Hypothesis

The selected representations must remain usable in the repository viewer. A separate content role does not
necessarily need a new screen, editor or custom rendering. Use retained pilot examples to establish which existing
navigation and artifact facilities work before deciding changes.

## 2. Technical Spike Questions

- **Q1**: Which entry, contract and supporting-file links already work for the selected representations?
- **Q2**: Which remaining gap needs viewer code rather than a corrected link, entry document or existing configuration?
- **Q3**: How should genuinely unsupported formats and missing files use existing viewing or download behavior?

## 3. Proposed Design & Impact

- Consume the delivered conventions; define no competing viewer-only schema. Use the retained domain, design
  and operational examples as post-implementation integration cases.
- Exercise concept-to-contract, contract-to-design-to-detail/artifact, and symptom-to-procedure/reference paths.
  Reuse generic document navigation and links. Existing facilities meeting the agreed paths pass without new UI.
- Implement only evidenced gaps in necessary navigation, labeling or artifact handling. Provide existing link or
  download behavior for unsupported formats rather than add spreadsheet editing or proprietary-format engines.
- If screens or interactions must change, draft them before code and reconcile their use cases and UX contracts.
  Keep implementation content out of UX documents. Do not create a separate editor or graph view for every role.

### Expected acceptance evidence

- The actual delivered representations reach the retained examples and supporting artifacts through their chosen
  entry points. Users need no guessed filesystem paths; existing document kinds retain usable navigation.
- Missing or unsupported artifacts have usable existing or changed behavior. Evidence distinguishes reused paths
  from required fixes; dedicated UI and runtime edits are conditional on observed failures.
- Changed frontend surfaces pass required frontend checks, and changed backend behavior has focused checks.
  If existing code suffices, navigation walkthrough evidence replaces unnecessary implementation work.

## 4. Lifecycle & Retirement Criteria

Start after the role conventions are delivered. Acceptance and handoff use the proposal gates. Retirement requires
verified navigation against actual retained examples and documentation of any required fixes. Together with the
lifecycle proposal, this supplies final integration evidence after the early content pilot.
