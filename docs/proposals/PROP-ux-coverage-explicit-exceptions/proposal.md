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
    - packages/devkit-docs/src/devkit_docs/features/governance/services/
    - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/ux_coverage/
    - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/ux_links/
    - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/
    - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/
    - docs/capabilities/governance/
    - docs/decisions/2026-11/20261102-ux-screens.md
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

- **Q1**: What is the smallest per-interaction and per-use-case-step notation that records a global or off-screen exception plus its reason without adding boilerplate to ordinary linked steps?
  - *Finding*: an inline marker at the item itself, in both documents. The Step cell of a global interaction starts with `global:` (any case) followed by the reason, an opaque text in place of the step pairs; an off-screen use case step holds the phrase `off screen: <reason>` (also `off-screen:`, any case) in one of its lines, the reason running to the end of that line. Ordinary linked rows and steps change nothing. A document-level declaration (a frontmatter map or an exceptions section keyed by step key or trigger label) was compared in `materials/notation-comparison.md`: it needs a key that drifts when steps are renumbered or a trigger is renamed, repeats what the item already says, and `ADR-ux-screens` already rejected a frontmatter map for the same reason. The inline marker follows the parser's own `resumes at <key>` precedent, needs no key and cannot go stale, which also closes Q2's removed-key case. Both markers are read by the shared model in `governance.services.ux`, so `RULE-ux-links` keeps treating a classified cell as an empty one without a change to its own module.
- **Q2**: How will malformed declarations, removed step keys and declarations attached to already linked items be diagnosed without silently disabling coverage?
  - *Finding*: a marker only replaces the gap report it covers when it carries a reason. `global:` with nothing after the colon keeps the row reported, with the message `interaction is classified global without a reason`; `off screen:` with nothing after it keeps the step reported, with `<UC> step <key> is classified off screen without a reason`; a step that both cites a UX ID and carries the phrase is reported as `<UC> step <key> is classified off screen but cites <UX>`. Every message stays a `RULE-ux-coverage` warning, so a defective classification is as visible as the gap it tried to cover and never quieter. A Step cell mixing pairs and `global:` is not a valid cell and stays a `RULE-ux-links` error through the existing cell check. There is no key to go stale: an inline marker is removed with its item. The two documents fail differently on a misspelling, and the record says so: a Step cell that is neither empty, pairs nor `global:` (`global nav`, `globl:`) is an invalid cell and a `RULE-ux-links` error today, as before this change; a misspelled step phrase (`offscreen:`) is not a marker, so the existing gap warning stays. The classified cell is defined by its prefix, so a reason may mention a step pair without becoming a mixed cell. Documents without markers keep every current warning; the severity override to `error` keeps raising all of them.
- **Q3**: Can findings point directly to the uncited use-case step rather than the first referencing UX document?
  - *Finding*: yes, within the same rule. Today the uncited step is reported on the first listing UX document the run targets and on the use case only when no listed UX document is in the run, so a whole-workspace run blames the navigation panel for every workflow gap. After this change the remediation (cite a screen or write `off screen: <reason>`) edits the use case, so the report is placed on the use case when the run targets it and only otherwise on the first listing UX document in the run, which keeps a run that touches only the UX document informed. The stepless-interaction report stays on the UX document. This replaces, for the uncited-step report only, the targeting clause of `ADR-ux-screens`; `PADR-ux-coverage-step-targeting` records it and is presented for the user's decision at `plan-accept` (withdrawn if declined).

## 3. Proposed Design & Impact

Retain the current distinction: missing coverage is a warning, contradictory links remain errors under RULE-ux-links. Add an explicit, reasoned way to classify only a particular interaction as global or a particular use-case step as off screen. Blank cells and uncited steps alone must not imply an exception. The classification must not bypass unknown IDs, invalid step references, reverse-link contradictions or reachability checks.

### Notation (`PADR-explicit-ux-coverage-exception-notation`)

- **Global interaction**: the Step cell, stripped, starts with `global:` (any case) followed by a non-empty reason; the row serves no step and the reason is opaque text (no pair is extracted from it). An empty cell is still allowed and still warns. A cell that starts with pairs and carries `global:` later, like any other cell that is neither empty, pairs nor `global:`, is an invalid Step cell (`RULE-ux-links`, unchanged).
- **Off-screen step**: a main-scenario step or extension holds `off screen: <reason>` (or `off-screen:`, any case) in one of its lines; the reason is the rest of that line, a trailing `)` and whitespace dropped. A step that carries the phrase and cites a UX ID is contradictory and is reported.
- **Reason**: free prose, non-empty; nothing judges its content, the owner does when reading the document. No heuristic on trigger or step wording. An off-screen reason names no screen: a code-span UX ID on the step's lines is a citation, so the step would be reported as contradictory and would join the flow graph; a step whose response appears on a screen cites that screen instead.
- **Flow effect**: a classified off-screen step keeps the flow effect of an uncited step (the screen before it needs no exit for it, the screen after it is an entry), and the coverage warning the `ADR-ux-screens` known limit relied on is gone for it; a wrong classification is caught only in review, which the threat model accepts.
- **Model**: `governance.services.ux` parses both markers once for both rules: `Interaction` learns whether its cell is a global classification and its reason, and `Step` whether it is classified off screen and its reason. `RULE-ux-links` reads unchanged fields and keeps every contradiction error; its module is excluded from this change.
- **Coverage rule**: a row classified global with a reason and a step classified off screen with a reason are not reported; the three defective forms in Q2 are reported with their own messages, at the same warning severity. The guide gains an Exceptions section naming both markers and the defective forms.
- **Targeting** (`PADR-ux-coverage-step-targeting`, user decision): the uncited-step report goes on the use case when the run targets it, else on the first listing UX document in the run.
- **Guidance**: `ux-writing` replaces "may leave the Step cell empty" with the `global:` form and keeps the empty cell as a warned gap; `usecase-writing` adds the `off screen:` phrase next to its off-screen sentence, with an example whose response reaches no screen and the rule that the reason names no screen; the `ux` template's Interactions comment shows the form; the `ux_links` guide and `CAP-GOV-spec-rules` 3.15 name the classified cell as an accepted Step cell; 3.16 and the rule table state the exceptions, the defective forms and the targeting. Development writes the "Superseded in part by" lines into `ADR-ux-screens` (handoff promotes the PADRs but writes no pointer); `.devkit/managed/` copies are regenerated by `devkit generated regen`, never edited.
- **Tests**: the rule's `tests/test_rule.py` gains fixtures modeled on the consumer evidence: a navigation screen with theme, skip-to-content and menu rows classified global beside an unclassified empty row, and a mail step classified off screen beside an unclassified system step; plus each defective form, a reason containing a step pair accepted, the mixed Step cell and a misspelled `global` cell staying `RULE-ux-links` errors, and the targeting cases (use case in the run, only the UX document in the run).

Expected affected contracts: `CAP-GOV-spec-rules` (3.1 table, 3.15, 3.16) and `ADR-ux-screens` (the coverage, the off-screen sentence and, if accepted, the targeting clause, each superseded in part). `docs/ux/README.md` and the `docs` bundle `AGENTS.md` are inspected at sync for the empty-cell wording. Changes stay in devkit-docs and its owned bundle assets; no consumer repository changes.

### Acceptance examples for Development

1. A theme toggle or skip-to-content interaction whose Step cell is `global: <reason>` produces no missing-Step warning; an unclassified blank row on the same screen still warns.
2. A genuine background-only step holding `off screen: <reason>` produces no missing-screen warning; an unclassified uncited step in the same use case still warns.
3. `global:` or `off screen:` without a reason, and an off-screen phrase on a step that cites a UX ID, are each reported with their own `RULE-ux-coverage` warning; a Step cell that starts with pairs and carries `global:` later, or misspells `global:`, stays a `RULE-ux-links` error, while `GLOBAL: <reason>` and a reason that mentions a step pair are accepted classifications.
4. A contradictory or nonexistent explicit UX/use-case link still fails its existing `RULE-ux-links` validation even when a coverage exception is present on the same document.
5. Existing documents and severity settings retain their behavior until an explicit classification is added. No heuristic based on label words such as "theme" or "background" is used.
6. Focused rule tests cover both accepted exceptions and negative controls; `ux-writing` and `usecase-writing` each demonstrate one valid example of their classification.
7. If `PADR-ux-coverage-step-targeting` is accepted: with every document in the run, the uncited step is reported on the use case at the step's line; with only the UX document in the run, on that document at its `usecases` entry.

### Planning decisions

- The "consumer example" of section 4 is satisfied by rule-test fixtures modeled on the consumer's navigation document and mail step; no consumer repository is changed by this proposal (Host decision within scope).
- The reason is validated only for presence. Judging its substance mechanically would need a heuristic, which section 3 forbids; the owner reads it in review.
- The shared model service (`governance.services.ux`) and the `ux_links` guide, the `ux` template and the `ADR-ux-screens` file are added to `boundaries.owns`, since the markers are parsed once for both rules and the acceptance adds "Superseded in part by" lines; `ux_links.py` stays excluded.
- Challenger round 1 (`envelopes/challenger-01.yaml`): findings 1-4 are folded above (case-insensitive prefix grammar for the cell, the corrected failure statement, the flow effect and the no-screen rule for reasons); findings 5 (a text-only edit of `ux_links.py`) and 6 (keeping `PADR-ux-coverage-step-targeting`) are decisions presented at `plan-accept`.
- `dev_effort` stays `medium`: the change touches a shared parser read by an error rule, with full fixture coverage; nothing is irreversible.

## 4. Lifecycle & Retirement Criteria

Planning settles the notation and validation contract above; ordinary acceptance and handoff create one feature spec. Completion requires maintained regression tests, synchronized guidance and the fixture-based example showing that genuine missing links remain visible while explicitly classified exceptions stop recurring.

Non-goals: making every coverage warning blocking, disabling coverage globally, weakening contradictory-link errors, adding runtime UI features, manufacturing use cases for global controls, or changing `ux_links.py`. Consumer documentation maintenance can proceed under existing rules; it does not depend on this proposal being implemented.
