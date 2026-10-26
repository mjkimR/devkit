---
id: SPEC-link-prefixes-and-milestone-remediation
title: Viewer ID link prefixes and milestone path remediation
summary: Fixes the viewer's document ID link pattern, which lists US instead of UC and lacks FB and MS, and the misplaced-milestone remediation, which tells a milestone to move to a dated partition.
status: in-progress
created: 2026-10-26
related_capabilities: [CAP-VIEW-repository-viewer, CAP-GOV-spec-rules]
related_usecases: []
workflow: sdd-spec-bugfix
---

# [SPEC-link-prefixes-and-milestone-remediation] Viewer ID link prefixes and milestone path remediation

## 1. Problem Statement & Motivation

Two small defects disagree with the document ID grammar that devkit-spec owns. The viewer's spec book links `[ID]`
references in prose only for a hard-coded prefix list that still names the retired `US` prefix and lacks `UC`, `FB`
and `MS`, so a reader of the Living Spec book sees use case, feedback and milestone references as plain text. The
`RULE-id-convention` remediation for a misplaced milestone tells an agent to move it into a dated
`{YYYY-MM}/{YYYYMMDD}-{slug}` partition, although milestones live flat under `docs/roadmap/`; an agent that follows
the directive moves the file to a location the same rule rejects. The user decided these are fixed in a separate
bugfix so the table-driven document kinds refactor stays output-identical (see `materials/defects.md`).

## 2. Defect Characterization

- **Current behavior**:
  - Viewer: `renderDocument` in `packages/devkit-viewer/frontend/src/lib/api/documents.ts` matches prose references
    with `/\[((?:CAP|US|ARCH|ADR|PROP|SPEC|PLAN|TASKS|REC|MAT|PADR)-...)\]/`. A document whose body contains
    `[UC-x]`, `[FB-x]` or `[MS-x]`, rendered with a document of that ID in the index, keeps the reference as plain
    text instead of a link.
  - Rule: `IdConventionRule._target` in
    `packages/devkit-spec/src/devkit_spec/features/governance/usecases/id_convention.py` chooses the remediation by
    `target.kind in _LIVING_SPEC` (capability, use case, architecture); every other kind, including
    `Kind.MILESTONE`, gets "Move the file to {YYYY-MM}/{YYYYMMDD}-{slug} with the decision or start date, then run
    `devkit rules fix`". A file `docs/misplaced.md` declaring `id: MS-misplaced`, or `docs/roadmap/MS-2026-q4.md`,
    receives that dated-partition remediation.
- **Expected behavior and its basis**:
  - Viewer: the linked prefixes are exactly the keys of `PREFIXES` in
    `packages/devkit-spec/src/devkit_spec/features/documents/models/ids.py` (`CAP`, `UC`, `ARCH`, `ADR`, `PROP`,
    `PADR`, `SPEC`, `PLAN`, `TASKS`, `REC`, `FB`, `MAT`, `MS`), the ID grammar of `CAP-DOCS-document-model`;
    `CAP-VIEW-repository-viewer` §4 promises in-page links between documents by ID.
  - Rule: a milestone must be stored at `docs/roadmap/MS-{slug}.md` (the rule's own path issue, and the rule guide's
    remediation step "for a Living Spec document or milestone, the ID is the file stem"), so the remediation names
    that location.
- **Behavior to preserve**:
  - A prose reference that resolves to no indexed document stays plain text; exact inline-code IDs, Markdown links
    and fenced code keep their current handling (`frontend/src/lib/documents.test.ts`).
  - Every non-milestone `RULE-id-convention` message and remediation stays byte-identical, including the dated
    partition remediation for ADR, spec bundle and feedback paths and the Living Spec remediation (rule tests in
    `rules/id_convention/tests/test_rule.py`).
- **Reproduction conditions**: `just viewer test` with a `renderDocument` call over a document whose body holds
  `[UC-a]`, `[FB-b]`, `[MS-c]` and indexed documents of those IDs; `just test devkit-spec` on the id_convention rule
  test with a misplaced milestone fixture, asserting the remediation text.

## 3. Non-Goals

1. **Scope Excluded**: the viewer ID character class (it keeps `[A-Za-z0-9-]`), deriving the viewer list from Python
   at build time, other kinds' rule messages, the rule guide text, and resolving the viewer link prefix feedback,
   which is not on this branch's base.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Prose references with every current prefix link
- **Given** a rendered document whose body holds `[UC-a]`, `[FB-b]` and `[MS-c]`, with documents of IDs UC-a, FB-b and MS-c indexed
- **When** `renderDocument` renders it
- **Then** the HTML holds 3 anchors, one per reference, each carrying its target's `data-doc-path`

### [AC-02] Retired and unresolved references stay plain text
- **Given** a rendered document whose body holds `[US-a]` with a document of ID `US-a` indexed, and `[UC-missing]` with none
- **When** `renderDocument` renders it
- **Then** the HTML holds no anchor and both references appear as text

### [AC-03] A misplaced milestone is told its real location
- **Given** `docs/misplaced.md` declaring `id: MS-misplaced` and `docs/roadmap/MS-2026-q4.md`
- **When** `RULE-id-convention` checks the workspace
- **Then** each milestone violation's remediation is exactly "Rename or move the file to docs/roadmap/MS-{slug}.md (the ID is the file stem), then run `devkit rules fix`"

### [AC-04] Other kinds' remediations are unchanged
- **Given** a misplaced ADR, spec feedback file and capability
- **When** `RULE-id-convention` checks the workspace
- **Then** the ADR and feedback remediations stay "Move the file to {YYYY-MM}/{YYYYMMDD}-{slug} with the decision or start date, then run `devkit rules fix`" and the capability remediation stays "Rename or move the file to the required path (the ID is the file stem), then run `devkit rules fix`"

## 5. Assumptions

- The viewer list is kept as a literal in the same order as `PREFIXES` rather than generated: the frontend has no
  build-time access to the Python grammar, and the defect asks only that the list match.
- `US-` IDs are invalid under the current grammar, so dropping `US` from the list loses no valid link.
