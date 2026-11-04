---
id: SPEC-ux-coverage-explicit-exceptions
title: Recognize explicit global and off-screen UX coverage exceptions
summary: Recognize reasoned global-control and off-screen exceptions in UX coverage without weakening missing-reference warnings or contradictory-link errors.
status: planned
created: 2026-11-04
related_capabilities:
  - CAP-GOV-spec-rules
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-ux-coverage-explicit-exceptions] Recognize explicit global and off-screen UX coverage exceptions

## 1. Problem Statement & Motivation

Handed off from proposal PROP-ux-coverage-explicit-exceptions on 2026-11-04; its decisions are
`ADR-explicit-ux-coverage-exception-notation` and `ADR-ux-coverage-step-targeting`, both superseding `ADR-ux-screens`
in part.
- **Preserved Materials**: `docs/materials/2026-11/20261104-ux-coverage-explicit-exceptions`

`ux-writing` lets a global control leave its Step cell empty and `usecase-writing` lets a step that happens off
screen cite no UX document, but `RULE-ux-coverage` (`CAP-GOV-spec-rules` 3.16) cannot tell an intended gap from a
forgotten one, so every intended gap warns on every run. In the consumer evidence (resource-indexer at commit
`09f1a8df0dffcf047da5efe2305dd3f6c7fc1058`) that is 40 warnings at once, 13 stepless interactions and 27 uncited
steps, of which the navigation document's theme, skip-to-content and small-screen menu rows and the background steps
are intended. The warnings stop separating defects from decisions, and the cheap way to silence one is an invented
citation that `RULE-ux-links` cannot tell from a true one. The uncited-step warnings also land on the first UX
document that lists the use case, so one navigation panel appears to own every workflow gap.

## 2. User Stories

- **US-1**: As an author of a UX document, I want to classify one interaction as a global control with a reason, so
  that `RULE-ux-coverage` stops warning for it while an unclassified empty Step cell still warns.
- **US-2**: As an author of a use case, I want to classify one step as happening off screen with a reason, so that
  the step stops warning while an unclassified uncited step still warns.
- **US-3**: As the owner reviewing a document, I want a classification without a reason, or one that contradicts a
  screen citation, reported as visibly as the gap it covers, so that no gap disappears silently.
- **US-4**: As an agent fixing coverage warnings, I want an uncited step reported on the use case I must edit, so
  that a navigation panel no longer carries unrelated workflow gaps.

## 3. Non-Goals

1. **Scope Excluded**: changing the logic of `RULE-ux-links` (only the docstring and the invalid-cell remediation
   text of `ux_links.py` change); any `RULE-ux-links` error stays an error.
2. **Scope Excluded**: a global disable of coverage, a severity change of `RULE-ux-coverage`, or a document-level
   exception list; the severity override to `error` keeps raising every report, classified-without-reason reports
   included.
3. **Scope Excluded**: any heuristic on trigger or step wording ("theme", "background") and any judgment of a
   reason's content; the reason is checked for presence only.
4. **Scope Excluded**: changes to consumer repositories; the consumer evidence is reproduced by rule-test fixtures.
5. **Scope Excluded**: a spelling check for near-miss step phrases (`offscreen:`); a follow-up of
   `ADR-explicit-ux-coverage-exception-notation` if consumers report it.

## 4. Acceptance Criteria & Behavioral Contracts

Fixtures: a use case UC-sign-in listed by the UX documents UX-login and UX-nav (both current, both in `docs/`);
`check(RULE, tmp_path, files, targets=...)` of `devkit_agt.features.rules.services.testing` runs a rule. Every
`RULE-ux-coverage` report is severity `warning`; every `RULE-ux-links` report is severity `error`.

### [AC-01] A global interaction with a reason is not reported
- **Given** UX-nav has the rows `| Toggle theme | global: a preference control that belongs to no task | ...`,
  `| Skip to content | GLOBAL: accessibility link on every screen | ...` and `| Open menu | global: the small-screen
  menu, independent of `UC-sign-in` 2 | ...` and one row whose Step cell is `` `UC-sign-in` 1 ``
- **When** `RULE-ux-coverage` runs with every document targeted
- **Then** it reports nothing for those three rows (`GLOBAL:` is accepted as any case; the pair inside the third
  reason is not read), and `RULE-ux-links` reports nothing for UX-nav

### [AC-02] An unclassified empty Step cell still warns
- **Given** UX-nav also has a row whose Step cell is `-`
- **When** `RULE-ux-coverage` runs
- **Then** it reports exactly one `interaction has no Step` on UX-nav at that row's line

### [AC-03] An off-screen step with a reason is not reported
- **Given** UC-sign-in step 2 is `The system sends the confirmation mail (`CAP-ACC-mail`). Off screen: the mail
  leaves by SMTP and nothing appears on a screen.` and extension 2a says `No mail (off-screen: the retry runs in the
  background); the use case ends.`
- **When** `RULE-ux-coverage` runs with every document targeted
- **Then** it reports nothing for step 2 or extension 2a (`Off screen:` and `off-screen:` both count; a closing `)`
  and the sentence period are not part of the reason)

### [AC-04] An unclassified uncited step still warns
- **Given** UC-sign-in step 3 cites no UX document and holds no phrase
- **When** `RULE-ux-coverage` runs with every document targeted
- **Then** it reports exactly one `UC-sign-in step 3 cites no UX document`

### [AC-05] A classification without a reason keeps the gap reported
- **Given** a UX-nav row whose Step cell is `global:` and a UC-sign-in step 4 that ends with `off screen:`
- **When** `RULE-ux-coverage` runs
- **Then** it reports `interaction is classified global without a reason` on UX-nav at the row's line and
  `UC-sign-in step 4 is classified off screen without a reason`, both severity `warning`, and no other report for
  those two items

### [AC-06] An off-screen phrase on a citing step is reported as contradictory
- **Given** UC-sign-in step 5 is `Opens `UX-login`; off screen: the result is cached.`
- **When** `RULE-ux-coverage` runs
- **Then** it reports `UC-sign-in step 5 is classified off screen but cites UX-login` (severity `warning`) and no
  `cites no UX document` report for step 5; `RULE-ux-links` treats step 5 as citing UX-login as before

### [AC-07] Invalid cells stay `RULE-ux-links` errors
- **Given** UX-nav rows whose Step cells are `` `UC-sign-in` 1, global: also a shortcut `` and `globl: typo`
- **When** `RULE-ux-links` runs
- **Then** it reports `Step cell "..." is not `UC-<slug>` <key>` for each (severity `error`), with a remediation
  naming `global: <reason>` beside the empty cell, and `RULE-ux-coverage` reports nothing for those rows

### [AC-08] Exceptions bypass no `RULE-ux-links` or `RULE-document-reference` check
- **Given** UX-nav holds a valid global row, a row whose Step cell is `` `UC-sign-in` 9 `` (no such step) and a row
  whose Step cell is `` `UC-ghost` 1 `` (no such document), and UX-login lists UC-sign-in while no Step cell names it
- **When** `RULE-ux-links` runs
- **Then** it reports `Step names UC-sign-in 9, which is not a step of UC-sign-in` and `usecases lists UC-sign-in,
  but no Step cell names it` exactly as without the global row, and nothing for UC-ghost: an unresolved ID is
  `RULE-document-reference`'s report (unchanged by this change) and `RULE-ux-links` skips it as before

### [AC-09] Documents without markers keep their reports, except for their placement
- **Given** the fixtures of the existing `RULE-ux-coverage` and `RULE-ux-links` tests, without any marker
- **When** both rules run
- **Then** every report of those tests still occurs with the same message and severity; only the file and line of
  the use-case-side `RULE-ux-coverage` reports change as AC-10 says, and `uv run devkit rules check` on this
  repository's `docs/` reports no new violation

### [AC-10] An uncited step is reported on its use case first
- **Given** UC-sign-in step 3 is uncited and UX-login and UX-nav both list UC-sign-in
- **When** `RULE-ux-coverage` runs with every document targeted
- **Then** it reports `UC-sign-in step 3 cites no UX document` once, on UC-sign-in at step 3's line
- **When** it runs with only UX-nav targeted
- **Then** it reports `UC-sign-in step 3 cites no UX document (<UC path>)` once, on UX-nav at its `usecases` entry
  line
- **When** it runs with only UC-sign-in targeted
- **Then** it reports it on UC-sign-in at step 3's line; the classified-without-reason and contradictory step
  reports of AC-05 and AC-06 follow the same placement, and `interaction has no Step` stays on the UX document

### [AC-11] Guidance and contracts demonstrate the notation
- **Given** the `docs` bundle sources
- **When** `grep -n "global:" packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/ux-writing.md
  packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/ux.md
  packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/ux_coverage/guide.md
  packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/ux_links/guide.md docs/capabilities/governance/CAP-GOV-spec-rules.md`
  and `grep -n -i "off screen:" packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/usecase-writing.md
  packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/ux_coverage/guide.md docs/capabilities/governance/CAP-GOV-spec-rules.md`
  run
- **Then** each named file has at least one hit, `ux-writing` and `usecase-writing` each contain one complete
  example row or step, and `uv run devkit generated check` and `uv run devkit sync --check` exit 0 after the
  managed copies are regenerated

## Assumptions

- A marker inside an inline code span of a step line counts like plain text (the line reader keeps code spans);
  nobody writes `` `off screen:` `` as prose, and the ADR's follow-up covers near misses.
- Two `off screen:` phrases in one step: the first found decides and its reason is read; no report.
- A `global:` cell on a `modal` or `panel` is accepted like on a `screen`.
- The targeting of AC-10 uses the run's `reportable()` set as today; `--staged` and `--ci` runs only narrow it.

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Technical Spike Questions

- **Q1**: What is the smallest per-interaction and per-use-case-step notation that records a global or off-screen exception plus its reason without adding boilerplate to ordinary linked steps?
  - *Finding*: an inline marker at the item itself, in both documents. The Step cell of a global interaction starts with `global:` (any case) followed by the reason, an opaque text in place of the step pairs; an off-screen use case step holds the phrase `off screen: <reason>` (also `off-screen:`, any case) in one of its lines, the reason running to the end of that line. Ordinary linked rows and steps change nothing. A document-level declaration (a frontmatter map or an exceptions section keyed by step key or trigger label) was compared in `docs/materials/2026-11/20261104-ux-coverage-explicit-exceptions/notation-comparison.md`: it needs a key that drifts when steps are renumbered or a trigger is renamed, repeats what the item already says, and `ADR-ux-screens` already rejected a frontmatter map for the same reason. The inline marker follows the parser's own `resumes at <key>` precedent, needs no key and cannot go stale, which also closes Q2's removed-key case. Both markers are read by the shared model in `governance.services.ux`, so `RULE-ux-links` keeps treating a classified cell as an empty one without a change to its logic; only its docstring and invalid-cell remediation text name the classified cell.
- **Q2**: How will malformed declarations, removed step keys and declarations attached to already linked items be diagnosed without silently disabling coverage?
  - *Finding*: a marker only replaces the gap report it covers when it carries a reason. `global:` with nothing after the colon keeps the row reported, with the message `interaction is classified global without a reason`; `off screen:` with nothing after it keeps the step reported, with `<UC> step <key> is classified off screen without a reason`; a step that both cites a UX ID and carries the phrase is reported as `<UC> step <key> is classified off screen but cites <UX>`. Every message stays a `RULE-ux-coverage` warning, so a defective classification is as visible as the gap it tried to cover and never quieter. A Step cell mixing pairs and `global:` is not a valid cell and stays a `RULE-ux-links` error through the existing cell check. There is no key to go stale: an inline marker is removed with its item. The two documents fail differently on a misspelling, and the record says so: a Step cell that is neither empty, pairs nor `global:` (`global nav`, `globl:`) is an invalid cell and a `RULE-ux-links` error today, as before this change; a misspelled step phrase (`offscreen:`) is not a marker, so the existing gap warning stays. The classified cell is defined by its prefix, so a reason may mention a step pair without becoming a mixed cell. Documents without markers keep every current warning; the severity override to `error` keeps raising all of them.
- **Q3**: Can findings point directly to the uncited use-case step rather than the first referencing UX document?
  - *Finding*: yes, within the same rule. Today the uncited step is reported on the first listing UX document the run targets and on the use case only when no listed UX document is in the run, so a whole-workspace run blames the navigation panel for every workflow gap. After this change the remediation (cite a screen or write `off screen: <reason>`) edits the use case, so the report is placed on the use case when the run targets it and only otherwise on the first listing UX document in the run, which keeps a run that touches only the UX document informed. The stepless-interaction report stays on the UX document. This replaces, for the uncited-step report only, the targeting clause of `ADR-ux-screens`; `ADR-ux-coverage-step-targeting` records it; the user kept it (answer-01, q1).

### 3. Proposed Design & Impact

Retain the current distinction: missing coverage is a warning, contradictory links remain errors under RULE-ux-links. Add an explicit, reasoned way to classify only a particular interaction as global or a particular use-case step as off screen. Blank cells and uncited steps alone must not imply an exception. The classification must not bypass unknown IDs, invalid step references, reverse-link contradictions or reachability checks.

#### Notation (`ADR-explicit-ux-coverage-exception-notation`)

- **Global interaction**: the Step cell, stripped, starts with `global:` (any case) followed by a non-empty reason; the row serves no step and the reason is opaque text (no pair is extracted from it). An empty cell is still allowed and still warns. A cell that starts with pairs and carries `global:` later, like any other cell that is neither empty, pairs nor `global:`, is an invalid Step cell (`RULE-ux-links`, unchanged).
- **Off-screen step**: a main-scenario step or extension holds `off screen: <reason>` (or `off-screen:`, any case) in one of its lines; the reason is the rest of that line, a trailing `)` and whitespace dropped. A step that carries the phrase and cites a UX ID is contradictory and is reported.
- **Reason**: free prose, non-empty; nothing judges its content, the owner does when reading the document. No heuristic on trigger or step wording. An off-screen reason names no screen: a code-span UX ID on the step's lines is a citation, so the step would be reported as contradictory and would join the flow graph; a step whose response appears on a screen cites that screen instead.
- **Flow effect**: a classified off-screen step keeps the flow effect of an uncited step (the screen before it needs no exit for it, the screen after it is an entry), and the coverage warning the `ADR-ux-screens` known limit relied on is gone for it; a wrong classification is caught only in review, which the threat model accepts.
- **Model**: `governance.services.ux` parses both markers once for both rules: `Interaction` learns whether its cell is a global classification and its reason, and `Step` whether it is classified off screen and its reason. `RULE-ux-links` reads unchanged fields and keeps every contradiction error; in `ux_links.py` only the module docstring and the invalid-cell remediation change, to name `global: <reason>` beside the empty cell (answer-01, q2); no logic of that rule changes.
- **Coverage rule**: a row classified global with a reason and a step classified off screen with a reason are not reported; the three defective forms in Q2 are reported with their own messages, at the same warning severity. The guide gains an Exceptions section naming both markers and the defective forms.
- **Targeting** (`ADR-ux-coverage-step-targeting`): the uncited-step report goes on the use case when the run targets it, else on the first listing UX document in the run; both guides and `CAP-GOV-spec-rules` 3.15/3.16 say why the two UX rules target the shared report differently.
- **Guidance**: `ux-writing` replaces "may leave the Step cell empty" with the `global:` form and keeps the empty cell as a warned gap; `usecase-writing` adds the `off screen:` phrase next to its off-screen sentence, with an example whose response reaches no screen and the rule that the reason names no screen; the `ux` template's Interactions comment shows the form; the `ux_links` guide and `CAP-GOV-spec-rules` 3.15 name the classified cell as an accepted Step cell; 3.16 and the rule table state the exceptions, the defective forms and the targeting. Development writes the "Superseded in part by" lines into `ADR-ux-screens` (handoff promotes the PADRs but writes no pointer); `.devkit/managed/` copies are regenerated by `devkit generated regen`, never edited.
- **Tests**: the rule's `tests/test_rule.py` gains fixtures modeled on the consumer evidence: a navigation screen with theme, skip-to-content and menu rows classified global beside an unclassified empty row, and a mail step classified off screen beside an unclassified system step; plus each defective form, a reason containing a step pair accepted, the mixed Step cell and a misspelled `global` cell staying `RULE-ux-links` errors, and the targeting cases (use case in the run, only the UX document in the run).

Expected affected contracts: `CAP-GOV-spec-rules` (3.1 table, 3.15, 3.16) and `ADR-ux-screens` (the coverage, the off-screen sentence and, if accepted, the targeting clause, each superseded in part). `docs/ux/README.md` and the `docs` bundle `AGENTS.md` are inspected at sync for the empty-cell wording. Changes stay in devkit-docs and its owned bundle assets; no consumer repository changes.

#### Acceptance examples for Development

1. A theme toggle or skip-to-content interaction whose Step cell is `global: <reason>` produces no missing-Step warning; an unclassified blank row on the same screen still warns.
2. A genuine background-only step holding `off screen: <reason>` produces no missing-screen warning; an unclassified uncited step in the same use case still warns.
3. `global:` or `off screen:` without a reason, and an off-screen phrase on a step that cites a UX ID, are each reported with their own `RULE-ux-coverage` warning; a Step cell that starts with pairs and carries `global:` later, or misspells `global:`, stays a `RULE-ux-links` error, while `GLOBAL: <reason>` and a reason that mentions a step pair are accepted classifications.
4. A contradictory explicit UX/use-case link (a wrong step key, a step that does not cite the document, an unlisted use case) still fails its existing `RULE-ux-links` validation even when a coverage exception is present on the same document; a nonexistent ID stays `RULE-document-reference`'s report, which this change does not touch.
5. Existing documents keep every warning they raise today, with its message and severity, until an explicit classification is added; only the placement of the use-case-side report changes (example 7). No heuristic based on label words such as "theme" or "background" is used.
6. Focused rule tests cover both accepted exceptions and negative controls; `ux-writing` and `usecase-writing` each demonstrate one valid example of their classification.
7. With every document in the run, the uncited step is reported on the use case at the step's line; with only the UX document in the run, on that document at its `usecases` entry.

#### Planning decisions

- The "consumer example" of section 4 is satisfied by rule-test fixtures modeled on the consumer's navigation document and mail step; no consumer repository is changed by this proposal (Host decision within scope).
- The reason is validated only for presence. Judging its substance mechanically would need a heuristic, which section 3 forbids; the owner reads it in review.
- The shared model service (`governance.services.ux`) and the `ux_links` guide, the `ux` template and the `ADR-ux-screens` file are added to `boundaries.owns`, since the markers are parsed once for both rules and the acceptance adds "Superseded in part by" lines. `ux_links.py` left `boundaries.excludes` on the user's decision (answer-01, q2): its docstring and remediation text may change, its logic may not.
- Challenger round 1 (historical Git `4f8cc73225c79629195b5343bc3ca9d585888626:docs/proposals/PROP-ux-coverage-explicit-exceptions/envelopes/challenger-01.yaml`): findings 1-4 are folded above (case-insensitive prefix grammar for the cell, the corrected failure statement, the flow effect and the no-screen rule for reasons); findings 5 (a text-only edit of `ux_links.py`) and 6 (keeping `ADR-ux-coverage-step-targeting`) were decided by the user in historical Git `4f8cc73225c79629195b5343bc3ca9d585888626:docs/proposals/PROP-ux-coverage-explicit-exceptions/envelopes/answer-01.yaml` and closed in `reverify-02`.
- `dev_effort` stays `medium`: the change touches a shared parser read by an error rule, with full fixture coverage; nothing is irreversible.

### 4. Lifecycle & Retirement Criteria

Planning settles the notation and validation contract above; ordinary acceptance and handoff create one feature spec. Completion requires maintained regression tests, synchronized guidance and the fixture-based example showing that genuine missing links remain visible while explicitly classified exceptions stop recurring.

Non-goals: making every coverage warning blocking, disabling coverage globally, weakening contradictory-link errors, adding runtime UI features, manufacturing use cases for global controls, or changing the logic of `ux_links.py`. Consumer documentation maintenance can proceed under existing rules; it does not depend on this proposal being implemented.

