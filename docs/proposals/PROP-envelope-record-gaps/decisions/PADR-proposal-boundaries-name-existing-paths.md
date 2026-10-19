---
id: PADR-proposal-boundaries-name-existing-paths
title: Proposal boundaries name existing paths
summary: Adds a devkit-spec rule that every target_area and boundaries.owns entry of a proposal resolves to an existing path, reporting the template placeholder under its own code.
proposal: PROP-envelope-record-gaps
status: draft
created_at: 2026-10-19
---

# [PADR-proposal-boundaries-name-existing-paths] Proposal boundaries name existing paths

- **Status**: Draft
- **Date**: 2026-10-19

---

## 1. Context & Problem Statement

`target_area` and `boundaries.owns` in `proposal.md` are free text. Nothing checks them when the proposal is created,
at `plan-intent` or at handoff, which copies them into the spec's carried notes and task boundary
(`proposals/handoff.py`, `proposals/specs.py`). A proposal declared `capabilities/core/`, an area that does not exist
(`FB-proposal-boundaries-unchecked`). `devkit spec proposal new` without `--target-area` writes the placeholder
`capabilities/<area>/` into both fields. Evidence: `materials/spike-evidence.md`.

## 2. Decision Drivers

- The current proposals use three forms (a bare area `delivery/`, a docs-root path `capabilities/delivery/` or
  `stories/delivery/`, a repository path `packages/...` or `docs/glossary.md`); all resolve today and none should need
  rewriting.
- A Backlog draft keeps the placeholder until Planning settles the area; its commits must not be refused.
- The boundary carried into Development must name real paths by `plan-accept`.
- A rule is not a gate or a policy: the commit gate already refuses error-severity violations.

## 3. Considered Options

- **A. A new rule `RULE-proposal-boundaries`** in the devkit-spec bundle, linter phase, with its guide and tests in its
  folder (`CAP-GOV-rule-authoring`).
- **B. More checks in `RULE-spec-format`**, which already validates the effort hints and `namespace` of proposal anchors.
- **C. A check in `devkit spec proposal handoff` only**: too late, after `plan-accept`.

## 4. Decision Outcome

- **Option A.** The rule reads every proposal anchor (`docs/proposals/PROP-<slug>/proposal.md` and single-file
  proposals) whose `status` is `draft`, `reviewing` or `accepted`; `rejected` proposals are skipped.
- Each `target_area` and `boundaries.owns` entry resolves when it names an existing file or directory, tried in this
  order: relative to the repository root, relative to the proposal's docs root (`docs/`, or the namespace docs root
  `docs/packages/<name>/` when `namespace` names one), and as a capability area `<docs root>/capabilities/<entry>`.
  `boundaries.excludes` is not checked.
- An entry with a `<...>` placeholder (the template's `capabilities/<area>/`) is reported as a placeholder, with its
  own message and fix (name the area), not as a missing path.
- Severity: placeholders and missing paths are warnings while the proposal is `draft`, and errors from `reviewing`
  on, so Planning settles them before `plan-accept` and the commit gate refuses an unsettled acceptance.
- Paths the Development will create: pending the user's answer to question `new-boundary-paths`.
- Not fixable: the rule cannot know the intended area.

## 5. Consequences

- devkit-spec: the rule, its guide and tests, its registration, the `spec` bundle's proposal template comment (the
  three accepted forms) and the Living Spec entry for proposal frontmatter (`CAP-DLV-proposal-incubation`) and the
  governance rule catalog.
- Proposals already `reviewing` on other `plan-` branches get an error at their next commit if an entry does not
  resolve; every current entry resolves (`materials/spike-evidence.md`).
